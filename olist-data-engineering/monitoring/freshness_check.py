"""Fail a scheduled job when the analytical fact table is stale.

Example:
    spark-submit monitoring/freshness_check.py \
      --fact-uri s3://YOUR-BUCKET/olist/warehouse/fact_order_items \
      --max-age-hours 30
"""

import argparse
import json
import sys
from datetime import datetime, timezone

from pyspark.sql import SparkSession, functions as F


def evaluate_freshness(fact_uri: str, max_age_hours: float) -> dict:
    spark = SparkSession.builder.appName("olist-freshness-check").getOrCreate()
    try:
        fact = spark.read.parquet(fact_uri)
        latest = fact.agg(F.max("loaded_at").alias("latest_loaded_at")).first()["latest_loaded_at"]
        if latest is None:
            return {"status": "failed", "reason": "fact table is empty", "fact_uri": fact_uri}

        if latest.tzinfo is None:
            latest = latest.replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - latest).total_seconds() / 3600
        return {
            "status": "passed" if age_hours <= max_age_hours else "failed",
            "latest_loaded_at": latest.isoformat(),
            "age_hours": round(age_hours, 2),
            "max_age_hours": max_age_hours,
            "fact_uri": fact_uri,
        }
    finally:
        spark.stop()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fact-uri", required=True)
    parser.add_argument("--max-age-hours", type=float, default=30.0)
    args = parser.parse_args()

    result = evaluate_freshness(args.fact_uri, args.max_age_hours)
    print(json.dumps(result, sort_keys=True))
    sys.exit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
