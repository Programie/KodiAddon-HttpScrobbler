import threading

from abc import ABC, abstractmethod
from typing import Callable


class ThreadLoop(threading.Thread, ABC):
    def __init__(self, wait_timeout: float = 1) -> None:
        super().__init__()

        self.wait_timeout = wait_timeout
        self.stop_event = threading.Event()

    def stop(self) -> None:
        self.stop_event.set()

    def run(self) -> None:
        self.on_start()

        while not self.stop_event.is_set():
            if not self.loop():
                self.stop_event.wait(self.wait_timeout)

        self.on_stop()

    @abstractmethod
    def loop(self) -> bool:
        pass

    def on_start(self) -> None:
        pass

    def on_stop(self) -> None:
        pass


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
