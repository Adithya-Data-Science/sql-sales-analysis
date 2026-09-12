# Market Data REST API Pipeline

A portfolio-grade Python data-engineering project that ingests public market candles from the Coinbase Exchange REST API, validates the response, de-duplicates overlapping windows, and upserts the cleaned records into a relational SQLite warehouse for SQL analysis. The project is intentionally read-only: it uses public market-data endpoints and does not place trades or require credentials.

## Why this project

It demonstrates the pieces expected in a production-oriented API integration workflow:

- REST API ingestion with request parameters, timeouts, retries, exponential backoff, and HTTP status handling;
- chunked extraction that respects Coinbase's documented maximum of 300 candles per request;
- schema normalization and data-quality checks for timestamps, OHLC consistency, and non-negative volume;
- idempotent relational loading with a composite primary key and SQL upserts;
- SQL analytics using aggregation and window functions;
- deterministic Pytest coverage with mocked HTTP responses; and
- Docker packaging for a reproducible runtime.

Coinbase documents the Exchange candle endpoint at `GET /products/{product_id}/candles`, supports specific granularity values, and notes that a request returns at most 300 candles. Historical market data can be incomplete, so this project treats the API as an external source that still requires validation.

## Architecture

```text
Coinbase Exchange REST API
        |
        v
Python API client
(retries + 300-candle windows)
        |
        v
Normalize + validate
(OHLC + volume + duplicate checks)
        |
        v
SQLite relational warehouse
(idempotent UPSERT)
        |
        v
SQL analytics / downstream ML features
```

## Repository structure

```text
coinbase-api-pipeline/
|-- src/
|   `-- pipeline.py
|-- tests/
|   `-- test_pipeline.py
|-- sql/
|   `-- analytics.sql
|-- Dockerfile
|-- requirements.txt
|-- .gitignore
`-- README.md
```

## Run locally

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python -m src.pipeline \
  --product BTC-USD \
  --start 2026-08-01T00:00:00Z \
  --end 2026-08-03T00:00:00Z \
  --granularity 3600 \
  --db data/market_data.db
```

The CLI prints how many rows were written and a warehouse summary. Re-running the same interval updates existing `(product_id, timestamp)` rows instead of creating duplicates.

## Run tests

```bash
pytest -q
```

Tests do not call the live Coinbase API. They mock HTTP responses so CI and local validation are repeatable.

## Run with Docker

```bash
docker build -t market-data-api-pipeline .
docker run --rm -v "${PWD}/data:/app/data" market-data-api-pipeline \
  --product BTC-USD \
  --start 2026-08-01T00:00:00Z \
  --end 2026-08-03T00:00:00Z \
  --granularity 3600 \
  --db data/market_data.db
```

## Example SQL analysis

After ingestion:

```bash
sqlite3 data/market_data.db < sql/analytics.sql
```

`analytics.sql` produces daily low/high prices, average close, total volume, and day-over-day closing-price change using a SQL window function.

## Engineering decisions

- **Reliability:** `requests.Session` uses retry/backoff for 429 and transient 5xx responses.
- **API limits:** long date ranges are split into windows of at most 300 candle intervals.
- **Data quality:** malformed rows, duplicate timestamps, negative values, and inconsistent OHLC fields fail validation.
- **Idempotency:** SQLite uses `(product_id, timestamp)` as the primary key and `ON CONFLICT ... DO UPDATE` for safe re-runs.
- **Security:** no API keys, secrets, account IDs, or trading permissions are required or stored.
- **Testability:** the HTTP client accepts an injectable session so unit tests can validate behavior without network access.

## Extension path

A production version could replace SQLite with PostgreSQL/Snowflake, orchestrate scheduled ingestion with Airflow, persist raw JSON for auditability, publish data-quality metrics, and stream real-time market events over WebSockets.
