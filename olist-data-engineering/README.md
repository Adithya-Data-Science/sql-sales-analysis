# Olist E-Commerce Data Engineering

A PySpark pipeline designed for AWS EMR that processes approximately 100,000 orders across eight linked public Olist datasets stored in Amazon S3.

## Pipeline

1. Read eight CSV datasets from an S3 prefix.
2. Check that required columns exist.
3. Deduplicate entity and order-item keys.
4. Aggregate one-to-many payment and review records before joining.
5. Join orders, items, customers, payments, reviews, products, sellers, and category translations.
6. Validate identifiers, duplicate keys, and negative prices.
7. Write analytics-ready Parquet output partitioned by order status.

## Data

Download the public Brazilian E-Commerce dataset by Olist from Kaggle and place these files under one local directory or S3 prefix:

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_customers_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `product_category_name_translation.csv`

Source data is excluded because of its size and should remain governed separately from code.

## Run locally

```bash
python -m venv .venv
python -m pip install -r requirements.txt
spark-submit spark_job.py --input-uri ./data/raw --output-uri ./data/processed
```

## Run on EMR

Upload the input CSVs and `spark_job.py` to S3, then submit the job as an EMR Spark step:

```bash
spark-submit spark_job.py \
  --input-uri s3://YOUR-BUCKET/olist/raw \
  --output-uri s3://YOUR-BUCKET/olist/processed
```

The script prints validation metrics before writing output and stops on nonzero duplicate/null/negative-price checks. `queries.sql` provides example Spark SQL KPI and reconciliation queries.

## Design notes

- Payments and reviews are aggregated before joining to avoid accidental row multiplication.
- Parquet reduces storage and scan costs compared with CSV.
- Partitioning by order status supports common operational filters.
- Bucket names are placeholders; no account IDs, credentials, or private paths are committed.
