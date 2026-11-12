import gzip
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from logstat.models import LogRecord
from logstat.parser import parse_line

@dataclass(slots=True)
class ParseStats:
    total: int = 0
    malformed: int = 0

def iter_records(path: Path , stats: ParseStats) -> Iterator[LogRecord]:
    if path.suffix == ".gz":
        fh = gzip.open(path, "rt", encoding="latin-1")
    else:
        fh = path.open("r", encoding="latin-1")
    with fh:
        for line in fh:
            stats.total +=1
            record = parse_line(line)
            if record is None:
                stats.malformed +=1
                continue
            yield record
