# Relational SQL ELT Warehouse

A small end-to-end data engineering project that loads two source-system CSV extracts into a validated relational warehouse and publishes BI-ready SQL queries.

## What this demonstrates
- Source-to-target ETL/ELT thinking and schema validation
- Relational database design with staging-style source files, a dimension table, and a fact table
- Primary keys, foreign keys, uniqueness checks, accepted values, and non-negative measures
- SQL joins, aggregations, and BI-ready outputs
- Automated end-to-end testing with a reproducible sample dataset

## Architecture
`customers.csv + orders.csv -> Python validation/load -> SQLite warehouse -> SQL analytics`

## Run from start to finish
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python pipeline.py --customers data/customers.csv --orders data/orders.csv --db data/warehouse.db
pytest -q
sqlite3 data/warehouse.db < analytics.sql
```

## Output model
- `dim_customers`: one row per source customer
- `fact_orders`: one row per order, linked through a surrogate customer key

## Data quality controls
The pipeline stops on duplicate business keys, unknown customer references, negative amounts, invalid statuses, missing required columns, or empty source files. It also runs a post-load referential-integrity check.

## Production extension
The same design can be moved from SQLite to SQL Server, PostgreSQL, Teradata, Oracle, MySQL, or Snowflake by replacing the connection/load layer while preserving the validation and source-to-target logic.
