import re
from datetime import datetime

from logstat.models import LogRecord

LINE_RE = re.compile(
    r'^(?P<host>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) (?P<proto>[^"]*)" '
    r'(?P<status>\d{3}) (?P<bytes>\d+|-)$'
)

TS_FORMAT = "%d/%b/%Y:%H:%M:%S %z"

def parse_line(line: str) -> LogRecord | None :
    match = LINE_RE.match(line.rstrip("\r\n"))
    if match is None:
        return None
    try:
        timestamp = datetime.strptime(match["ts"], TS_FORMAT)
    except ValueError:
        return None
    raw_bytes = match["bytes"]

    return LogRecord(
        host=match["host"],
        timestamp=timestamp,
        method=match["method"],
        path=match["path"],
        protocol=match["proto"],
        status=int(match["status"]),
        bytes_sent= None  if raw_bytes == "-" else int(raw_bytes)
    )