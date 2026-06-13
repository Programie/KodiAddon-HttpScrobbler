import json
import queue
import sqlite3
import requests
import threading
import xbmc

from abc import abstractmethod, ABC
from dataclasses import dataclass
from pathlib import Path
from requests.auth import AuthBase

from resources.lib.enums import Status, EventType


@dataclass
class QueueItem:
    id: int
    status: Status
    event: dict


class Database:
    def __init__(self, file_path: Path) -> None:
        self.lock = threading.Lock()
        self.connection = sqlite3.connect(file_path, check_same_thread=False)

        self.connection.row_factory = sqlite3.Row

        self.connection.execute("PRAGMA journal_mode=WAL;")
        self.connection.execute("PRAGMA synchronous=NORMAL;")
        self.connection.execute("PRAGMA temp_store=MEMORY;")

    def init_db(self) -> None:
        # @formatter:off
        query = """
            CREATE TABLE IF NOT EXISTS event_queue
            (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                type       TEXT    NOT NULL,
                payload    TEXT    NOT NULL,
                created_at INTEGER NOT NULL,
                status     INTEGER NOT NULL
            );

            CREATE INDEX IF NOT EXISTS event_queue_session ON event_queue (session_id);
        """
        # @formatter:on

        self.connection.executescript(query)

    def close(self) -> None:
        self.connection.close()

    def execute_write_query(self, query: str, params: dict | None = None) -> None:
        with self.lock:
            self.connection.execute(query, params or {})
            self.connection.commit()

    def execute_read_query(self, query: str, params: dict | None = None) -> sqlite3.Cursor:
        return self.connection.execute(query, params or {})

    def clear_session(self, session_id: str) -> None:
        self.execute_write_query("DELETE FROM event_queue WHERE session_id = :session_id", {"session_id": session_id})

    def add_event(self, event_data: dict) -> None:
        self.execute_write_query("INSERT INTO event_queue (session_id, type, payload, created_at, status) VALUES (:session_id, :type, :payload, :created_at, :status)", {
            "session_id": event_data.get("sessionId"),
            "type": event_data.get("event"),
            "payload": json.dumps(event_data),
            "created_at": event_data.get("timestamp"),
            "status": Status.PENDING.value
        })

    def claim_next_event(self) -> QueueItem | None:
        row = self.execute_read_query("SELECT id, payload FROM event_queue WHERE status = :status ORDER BY id ASC LIMIT 1", {"status": Status.PENDING.value}).fetchone()
        if not row:
            return None

        self.execute_write_query("UPDATE event_queue SET status = :status WHERE id = :id", {"status": Status.PROCESSING.value, "id": row["id"]})

        return QueueItem(id=row["id"], status=Status.PROCESSING, event=json.loads(row["payload"]))

    def mark_as_done(self, event_id: int) -> None:
        self.execute_write_query("DELETE FROM event_queue WHERE id = :id", {"id": event_id})

    def mark_as_failed(self, event_id: int) -> None:
        self.execute_write_query("UPDATE event_queue SET status = :status WHERE id = :id", {"status": Status.FAILED.value, "id": event_id})

    def mark_as_skipped(self, session_id: str) -> None:
        self.execute_write_query("UPDATE event_queue SET status = :status WHERE session_id = :session_id", {"status": Status.SKIPPED.value, "session_id": session_id})

    def mark_failed_as_pending(self):
        self.execute_write_query("UPDATE event_queue SET status = :pending_status WHERE status = :failed_status", {"pending_status": Status.PENDING.value, "failed_status": Status.FAILED.value})


class ThreadLoop(threading.Thread, ABC):
    def __init__(self) -> None:
        super().__init__()

        self.stop_event = threading.Event()

    def stop(self) -> None:
        self.stop_event.set()

    def run(self) -> None:
        self.on_start()

        while not self.stop_event.is_set():
            if not self.loop():
                self.stop_event.wait(1)

        self.on_stop()

    @abstractmethod
    def loop(self) -> bool:
        pass

    def on_start(self) -> None:
        pass

    def on_stop(self) -> None:
        pass


class QueueHandler(ThreadLoop):
    def __init__(self, database_filepath: Path) -> None:
        super().__init__()

        self.database = Database(database_filepath)
        self.database.init_db()

        # Queues
        self.input_queue: queue.Queue[dict] = queue.Queue()
        self.request_queue: queue.Queue[QueueItem] = queue.Queue()
        self.response_queue: queue.Queue[QueueItem] = queue.Queue()

    def loop(self) -> bool:
        return max(
            self.process_input_queue(),
            self.process_request_queue(),
            self.process_response_queue()
        )

    def on_start(self) -> None:
        # Mark failed events as pending to retry them
        self.database.mark_failed_as_pending()

    def on_stop(self) -> None:
        self.database.close()

    def add_event(self, event_data: dict) -> None:
        self.input_queue.put(event_data)

    def process_input_queue(self) -> bool:
        try:
            event = self.input_queue.get_nowait()

            self.database.add_event(event)

            return True
        except queue.Empty:
            return False

    def process_request_queue(self) -> bool:
        queue_item = self.database.claim_next_event()
        if not queue_item:
            return False

        self.request_queue.put(queue_item)
        return True

    def process_response_queue(self) -> bool:
        try:
            queue_item = self.response_queue.get_nowait()

            if queue_item.status == Status.DONE:
                self.database.mark_as_done(queue_item.id)

                # Mark any remaining events of the same session as skipped to prevent resending them automatically
                session_id: str | None = queue_item.event.get("sessionId")
                if EventType(queue_item.event.get("event")) in [EventType.STOP, EventType.END] and session_id:
                    self.database.mark_as_skipped(session_id)
            else:
                self.database.mark_as_failed(queue_item.id)

            return True
        except queue.Empty:
            return False


class HTTPWorker(ThreadLoop):
    def __init__(self, request_queue: queue.Queue[QueueItem], response_queue: queue.Queue[QueueItem]) -> None:
        super().__init__()

        self.request_queue = request_queue
        self.response_queue = response_queue

        self.url: str | None = None
        self.auth: AuthBase | None = None

    def loop(self) -> bool:
        if not self.url:
            return False

        try:
            queue_item = self.request_queue.get_nowait()

            if self.process_request(queue_item.event):
                queue_item.status = Status.DONE
                self.response_queue.put(queue_item)
            else:
                queue_item.status = Status.FAILED
                self.response_queue.put(queue_item)

            return True
        except queue.Empty:
            return False

    def process_request(self, event_data: dict) -> bool:
        xbmc.log(f"Sending data to URL {self.url}: {event_data}", level=xbmc.LOGINFO)

        try:
            response = requests.post(url=str(self.url), json=event_data, auth=self.auth, timeout=5)
            response.raise_for_status()
            return True
        except Exception as exception:
            xbmc.log(f"Request failed for URL {self.url}: {exception}", level=xbmc.LOGERROR)
            return False


class QueueProcessor:
    def __init__(self, database_filepath: Path) -> None:
        self.queue_handler = QueueHandler(database_filepath)
        self.http_worker = HTTPWorker(request_queue=self.queue_handler.request_queue, response_queue=self.queue_handler.response_queue)

    def start(self) -> None:
        self.queue_handler.start()
        self.http_worker.start()

    def stop(self) -> None:
        self.queue_handler.stop()
        self.http_worker.stop()

    def join(self) -> None:
        self.queue_handler.join()
        self.http_worker.join()
