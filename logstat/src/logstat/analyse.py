from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import timezone

from logstat.models import LogRecord

@dataclass(slots=True)
class Aggregates:
    top_path: list[tuple[str,int]]
    status_counts:dict[str,int]
    requests_per_hour: dict[str,int]

def aggregate(records: Iterable[LogRecord], top_n: int = 10) -> Aggregates:
    paths: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    hours: defaultdict[str,int] = defaultdict(int)

    for rec in records:
        paths[rec.path] += 1
        statuses[str(rec.status)] += 1
        hour = rec.timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:00")
        hours[hour] += 1

    return Aggregates(
       top_path=paths.most_common(top_n),
       status_counts=dict(sorted(statuses.items())),
       requests_per_hour=dict(sorted(hours.items()))        
   )