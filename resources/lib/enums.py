from enum import IntEnum, StrEnum


class EventType(StrEnum):
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    END = "end"
    SEEK = "seek"
    INTERVAL = "interval"


class Status(IntEnum):
    DONE = 0
    PENDING = 1
    PROCESSING = 2
    FAILED = 3
    SKIPPED = 4
