# Scheduled Multi-Source ETL Integration

A schedule-ready ETL integration that extracts from two different file-system sources (CSV and JSON), validates and reconciles them, and loads an idempotent relational database for downstream reporting.

## What this demonstrates
- Extraction from multiple source formats
- Schema validation and cross-source referential checks
- Idempotent relational loading with primary keys and SQL upserts
- Execution logging and repeatable reruns
- Automated tests for end-to-end row counts and reconciliation
- A PowerShell entry point suitable for Windows Task Scheduler

## Architecture
`CSV source + JSON source -> validation/reconciliation -> SQLite integration tables -> downstream reporting`

## Run from start to finish
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python etl.py --assets data/assets.csv --usage data/usage.json --db data/integration.db --log data/etl.log
pytest -q
```

## Scheduling
`run_etl.ps1` is the scheduler entry point. In Windows Task Scheduler, configure a recurring task to run PowerShell with this script. The ETL is idempotent, so re-running the same source window updates matching business keys rather than duplicating rows.

## Data quality controls
The integration rejects missing schemas, negative hours, and usage rows whose asset IDs are absent from the master source. SQLite constraints enforce non-negative measures and unique `(asset_id, usage_date)` records.

## Production extension
A production deployment could use SQL Server/Snowflake as the target and an enterprise scheduler or orchestration platform while keeping the same source validation, idempotency, logging, and test patterns.
