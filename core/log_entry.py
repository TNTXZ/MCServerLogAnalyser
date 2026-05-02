from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    INFO = "INFO"
    DEBUG = "DEBUG"
    WARN = "WARN"
    ERROR = "ERROR"


@dataclass
class LogEntry:
    timestamp: datetime
    level: LogLevel
    thread: str
    message: str
    raw_line: str
    line_number: int
    marked: bool = False
