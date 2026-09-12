# Olist Data Engineering, Customer Growth, and Operations Analytics

A PySpark and Spark SQL project designed for AWS EMR that processes approximately 100,000 orders across eight linked public Olist datasets stored in Amazon S3.

## Purpose and findings

The project turns fragmented order, item, customer, payment, review, product, seller, and category files into a validated integration layer and dimensional warehouse for operations and customer-growth decisions. Comparing promised and actual delivery dates with review scores showed that late deliveries aligned with lower customer satisfaction, identifying delivery exceptions as a useful service-recovery and fulfillment-monitoring signal.

## Architecture

1. Read eight CSV datasets from an S3 prefix and verify required columns.
2. Deduplicate entity and order-item keys.
3. Aggregate one-to-many payment and review records before joining.
4. Validate identifiers, duplicate keys, and nonnegative measures.
5. Write the integrated `olist_order_items` Parquet layer.
6. Build a star schema at order-item grain:
   - `fact_order_items`
   - `dim_customers`
   - `dim_products`
   - `dim_sellers`
   - `dim_date`
7. Run SQL assertions for uniqueness, not-null rules, accepted values, measure reconciliation, and referential integrity.
8. Run a configurable freshness monitor that emits machine-readable JSON and exits nonzero for a stale or empty fact table.

See [LINEAGE.md](LINEAGE.md) for the source-to-model map, grain, keys, downstream consumers, ownership, and freshness contract.

## Dimensional modeling

[`models/star_schema.sql`](models/star_schema.sql) defines the warehouse models. The fact table contains one row per `order_id + order_item_id`; deterministic SHA-256 keys support repeatable rebuilds, while natural identifiers are retained for traceability. Dimensions centralize customer, product, seller, and calendar attributes so analysts do not need to reproduce multi-source joins.

## Data quality and monitoring

[`tests/data_quality_tests.sql`](tests/data_quality_tests.sql) contains executable assertions that must return zero rows. Tests cover:

- duplicate fact grain;
- required keys and nonnegative measures;
- customer, product, seller, and date referential integrity;
- item-revenue reconciliation;
- accepted review-score values.

[`monitoring/freshness_check.py`](monitoring/freshness_check.py) evaluates `loaded_at` against a configurable service-level threshold. Its nonzero failure exit can be connected to EMR orchestration, a scheduler, or CI alerting.

```bash
spark-submit monitoring/freshness_check.py \
  --fact-uri s3://YOUR-BUCKET/olist/warehouse/fact_order_items \
  --max-age-hours 30
```

## Operations and customer-growth analysis

- `queries.sql` reports delivered-order KPIs and reconciles payment totals against item and freight totals.
- `customer_growth_analysis.sql` calculates repeat-customer rate, average customer value, recent high-value customers, re-engagement candidates, and review scores by state.
- The customer query creates an outreach structure using de-identified external customer IDs and honest segment labels.
- The source data has no email or phone fields, so the project does not invent contact information or claim direct Salesforce administration.

## Data

Download the public Brazilian E-Commerce dataset by Olist from Kaggle and place the eight source CSV files under one local directory or S3 prefix. Source data is excluded because of its size and should remain governed separately from code.

## Run the integration pipeline

```bash
python -m venv .venv
python -m pip install -r requirements.txt
spark-submit spark_job.py --input-uri ./data/raw --output-uri ./data/processed
```

For EMR, replace the local paths with governed S3 prefixes. The script prints validation metrics before writing output and stops on nonzero duplicate, null, or negative-price checks.

## Design notes

- Payments and reviews are aggregated before joining to prevent row multiplication.
- The star schema makes grain and reusable business dimensions explicit.
- Parquet reduces storage and scan costs compared with CSV.
- SQL assertions block invalid models before downstream publication.
- The freshness monitor provides a production-style interface for scheduled alerting.
- Bucket names are placeholders; no account IDs, credentials, private paths, or institutional records are committed.

## Execution status

The original AWS EMR integration-pipeline run was completed in 2026 against the eight Olist datasets stored in Amazon S3. The dimensional models, SQL tests, lineage documentation, and freshness monitor are reproducible portfolio extensions; this repository does not claim that those later extensions were executed in the original EMR run. See [VERIFICATION.md](VERIFICATION.md) for the verification scope and disclosure limits.
