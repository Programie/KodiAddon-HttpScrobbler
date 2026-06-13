import threading

from typing import Callable


class Timer(threading.Thread):
    def __init__(self, interval: int, callback: Callable) -> None:
        super().__init__()

        self.interval = interval
        self.callback = callback
        self.stop_event = threading.Event()

    def stop(self) -> None:
        self.stop_event.set()

    def run(self) -> None:
        while not self.stop_event.is_set():
            if self.stop_event.wait(self.interval):
                break

            self.callback()
