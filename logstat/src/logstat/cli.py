import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import typer

from logstat.analyse import aggregate
from logstat.models import LogRecord
from logstat.reader import ParseStats, iter_records 

app = typer.Typer(add_completion=False, help="Logstat is a tool for analyzing web server logs.")

@app.command()
def summarise(
    path: Annotated[Path, typer.Argument(exists=True, readable=True, dir_okay=False, resolve_path=True)],
    top: Annotated[int, typer.Option(min=1, help="Number of top paths to display.")] = 10,
) -> None:
    stats = ParseStats()
    agg = aggregate(iter_records(path, stats), top_n=top)
    report = {"lines":stats.total, "malformed":stats.malformed, **asdict(agg)}
    typer.echo(json.dumps(report, indent=4))