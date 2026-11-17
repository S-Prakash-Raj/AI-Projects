from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Settings:
    start_url: str = "https://localhost:8000/page0.html"
    max_pages: int = 500
    concurrency: int = 20
    rps_per_host: int = 10.0
    brust: float = 5.0
    timeout: float = 5.0
    max_retires: int = 3
    backoff: float = 0.5
output_path: str = "results.json"