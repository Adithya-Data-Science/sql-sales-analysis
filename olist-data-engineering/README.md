# Olist Data Engineering, Customer Growth, and Operations Analytics

A PySpark and Spark SQL project designed for AWS EMR that processes approximately 100,000 orders across eight linked public Olist datasets stored in Amazon S3.

## Purpose and findings

The project turns fragmented order, item, customer, payment, review, product, seller, and category files into a validated analytical layer for operations and customer-growth decisions. Comparing promised and actual delivery dates with review scores showed that late deliveries aligned with lower customer satisfaction, identifying delivery exceptions as a useful service-recovery and fulfillment-monitoring signal. The analysis also produces regional growth KPIs and loyalty, re-engagement, and service-recovery segments for reporting and outreach planning.

## Pipeline

1. Read eight CSV datasets from an S3 prefix.
2. Check that required columns exist.
3. Deduplicate entity and order-item keys.
4. Aggregate one-to-many payment and review records before joining.
5. Join orders, items, customers, payments, reviews, products, sellers, and category translations.
6. Validate identifiers, duplicate keys, and negative prices.
7. Write analytics-ready Parquet output partitioned by order status.

## Operations and customer-growth analysis

- `queries.sql` reports delivered-order KPIs and reconciles payment totals against item and freight totals.
- `customer_growth_analysis.sql` calculates repeat-customer rate, average customer value, recent high-value customers, re-engagement candidates, and review scores by state.
- The customer query creates a Salesforce-ready outreach structure using de-identified external customer IDs and honest segment labels.
- The source data has no email or phone fields, so the project does not invent contact information or claim direct Salesforce administration.

## Data

Download the public Brazilian E-Commerce dataset by Olist from Kaggle and place the eight source CSV files under one local directory or S3 prefix. Source data is excluded because of its size and should remain governed separately from code.

## Run locally

```bash
python -m venv .venv
python -m pip install -r requirements.txt
spark-submit spark_job.py --input-uri ./data/raw --output-uri ./data/processed
```

## Run on EMR

```bash
spark-submit spark_job.py \
  --input-uri s3://YOUR-BUCKET/olist/raw \
  --output-uri s3://YOUR-BUCKET/olist/processed
```

The script prints validation metrics before writing output and stops on nonzero duplicate/null/negative-price checks.

## Design notes

- Payments and reviews are aggregated before joining to avoid accidental row multiplication.
- Parquet reduces storage and scan costs compared with CSV.
- Partitioning by order status supports common operational filters.
- Bucket names are placeholders; no account IDs, credentials, or private paths are committed.

## Execution status

The AWS EMR pipeline run was completed in 2026 against the eight Olist datasets stored in Amazon S3. The source bucket and account-specific paths remain private. See [VERIFICATION.md](VERIFICATION.md) for the verification scope and disclosure limits.
