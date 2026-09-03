"""Build validated, analytics-ready Olist order data with PySpark."""

import argparse

from pyspark.sql import DataFrame, SparkSession, functions as F


DATASETS = {
    "orders": "olist_orders_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def read_csv(spark: SparkSession, uri: str) -> DataFrame:
    return spark.read.option("header", True).option("inferSchema", True).csv(uri)


def require_columns(df: DataFrame, dataset: str, columns: set[str]) -> None:
    missing = columns.difference(df.columns)
    if missing:
        raise ValueError(f"{dataset} is missing required columns: {sorted(missing)}")


def load_inputs(spark: SparkSession, input_uri: str) -> dict[str, DataFrame]:
    frames = {
        name: read_csv(spark, f"{input_uri.rstrip('/')}/{filename}")
        for name, filename in DATASETS.items()
    }
    required = {
        "orders": {"order_id", "customer_id", "order_status", "order_purchase_timestamp"},
        "items": {"order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"},
        "customers": {"customer_id", "customer_unique_id", "customer_state"},
        "payments": {"order_id", "payment_value"},
        "reviews": {"order_id", "review_score"},
        "products": {"product_id", "product_category_name"},
        "sellers": {"seller_id", "seller_state"},
        "category_translation": {"product_category_name", "product_category_name_english"},
    }
    for name, columns in required.items():
        require_columns(frames[name], name, columns)
    return frames


def aggregate_one_to_many(frames: dict[str, DataFrame]) -> dict[str, DataFrame]:
    frames["payments"] = frames["payments"].groupBy("order_id").agg(
        F.round(F.sum("payment_value"), 2).alias("payment_total")
    )
    frames["reviews"] = frames["reviews"].groupBy("order_id").agg(
        F.round(F.avg("review_score"), 2).alias("average_review_score")
    )
    return frames


def build_order_items(frames: dict[str, DataFrame]) -> DataFrame:
    orders = frames["orders"].dropDuplicates(["order_id"]).withColumn(
        "order_purchase_timestamp", F.to_timestamp("order_purchase_timestamp")
    )
    customers = frames["customers"].dropDuplicates(["customer_id"])
    products = frames["products"].dropDuplicates(["product_id"])
    sellers = frames["sellers"].dropDuplicates(["seller_id"])
    translations = frames["category_translation"].dropDuplicates(["product_category_name"])

    return (
        frames["items"]
        .dropDuplicates(["order_id", "order_item_id"])
        .join(orders, "order_id", "inner")
        .join(customers, "customer_id", "left")
        .join(products, "product_id", "left")
        .join(translations, "product_category_name", "left")
        .join(sellers, "seller_id", "left")
        .join(frames["payments"], "order_id", "left")
        .join(frames["reviews"], "order_id", "left")
        .withColumn("item_revenue", F.round(F.col("price") + F.col("freight_value"), 2))
    )


def validate_output(df: DataFrame) -> dict[str, int]:
    metrics = {
        "row_count": df.count(),
        "null_order_ids": df.filter(F.col("order_id").isNull()).count(),
        "duplicate_order_items": (
            df.groupBy("order_id", "order_item_id").count().filter(F.col("count") > 1).count()
        ),
        "negative_prices": df.filter(F.col("price") < 0).count(),
    }
    failures = {name: value for name, value in metrics.items() if name != "row_count" and value != 0}
    if failures:
        raise ValueError(f"Output validation failed: {failures}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-uri", required=True, help="S3 prefix or local directory containing the CSV files")
    parser.add_argument("--output-uri", required=True, help="S3 prefix or local directory for Parquet outputs")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("olist-data-engineering").getOrCreate()
    try:
        frames = aggregate_one_to_many(load_inputs(spark, args.input_uri))
        order_items = build_order_items(frames).cache()
        metrics = validate_output(order_items)
        for name, value in metrics.items():
            print(f"VALIDATION {name}={value}")

        order_items.write.mode("overwrite").partitionBy("order_status").parquet(
            f"{args.output_uri.rstrip('/')}/order_items"
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
