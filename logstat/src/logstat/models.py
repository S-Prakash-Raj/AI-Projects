from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots =True)
class LogRecord:
    host: str
    timestamp: datetime
    method: str
    path :str
    protocol: str
    status:int
    bytes_sent: int | None

