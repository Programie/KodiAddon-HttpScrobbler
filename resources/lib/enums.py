from enum import Enum, IntEnum


class EventType(str, Enum):
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    END = "end"
    SEEK = "seek"
    INTERVAL = "interval"

    def __str__(self) -> str:
        return self.value


class Status(IntEnum):
    DONE = 0
    PENDING = 1
    PROCESSING = 2
    FAILED = 3
    SKIPPED = 4
