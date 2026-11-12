# logstat

A small CLI for analysing web server access logs in Common Log Format. It reads plain or gzip-compressed (`.gz`) logs and prints a JSON summary with:

- total and malformed line counts
- the most requested paths
- counts per HTTP status code
- requests per hour (UTC)

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
uv sync
```

## Getting the sample data (NASA HTTP logs)

The project is built and tested against the public **NASA Kennedy Space Center HTTP logs** from July 1995. They're hosted by the Internet Traffic Archive: <https://ita.ee.lbl.gov/html/contrib/NASA-HTTP.html>

| File | Period | Size (compressed) |
|------|--------|-------------------|
| `NASA_access_log_Jul95.gz` | 1–31 July 1995 | ~20 MB |
| `NASA_access_log_Aug95.gz` | 1–31 August 1995 | ~16 MB |

Download the July log into the project root:

```bash
curl -O https://ita.ee.lbl.gov/traces/NASA_access_log_Jul95.gz
```

Or with `wget`:

```bash
wget https://ita.ee.lbl.gov/traces/NASA_access_log_Jul95.gz
```

For the August log, use `NASA_access_log_Aug95.gz` in the same URL.

You don't need to decompress it, because logstat reads `.gz` files directly. If you want to look at the raw lines:

```bash
gunzip -c NASA_access_log_Jul95.gz | head
```

Each line follows Common Log Format:

```
199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245
```

> The log files are large and shouldn't be committed. Add `*.gz` to `.gitignore`.

## Usage

```bash
uv run logstat NASA_access_log_Jul95.gz
```

Show the top 5 paths instead of the default 10:

```bash
uv run logstat NASA_access_log_Jul95.gz --top 5
```

Example output for `--top 3` on the July log (`requests_per_hour` is cut short here):

```json
{
    "lines": 1891715,
    "malformed": 2929,
    "top_path": [
        ["/images/NASA-logosmall.gif", 111144],
        ["/images/KSC-logosmall.gif", 89530],
        ["/images/MOSAIC-logosmall.gif", 60300]
    ],
    "status_counts": {
        "200": 1698705, "302": 46550, "304": 132627,
        "403": 54, "404": 10774, "500": 62, "501": 14
    },
    "requests_per_hour": {
        "1995-07-01 04:00": 3558,
        "1995-07-01 05:00": 2989,
        "...": "..."
    }
}
```

## Development

Run the tests:

```bash
uv run pytest
```

Type-check:

```bash
uv run mypy
```
