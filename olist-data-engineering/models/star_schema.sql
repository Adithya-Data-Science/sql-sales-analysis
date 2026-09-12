-- Olist analytics star schema (Spark SQL)
-- Grain: one row in fact_order_items per source order_id + order_item_id.
-- Natural keys are retained for traceability; deterministic SHA-256 keys provide
-- stable warehouse joins across idempotent rebuilds.

CREATE OR REPLACE TABLE dim_date
USING PARQUET AS
SELECT DISTINCT
    CAST(date_format(order_purchase_timestamp, 'yyyyMMdd') AS INT) AS date_key,
    CAST(order_purchase_timestamp AS DATE) AS calendar_date,
    year(order_purchase_timestamp) AS calendar_year,
    quarter(order_purchase_timestamp) AS calendar_quarter,
    month(order_purchase_timestamp) AS calendar_month,
    day(order_purchase_timestamp) AS day_of_month,
    dayofweek(order_purchase_timestamp) AS day_of_week
FROM olist_order_items
WHERE order_purchase_timestamp IS NOT NULL;

CREATE OR REPLACE TABLE dim_customers
USING PARQUET AS
SELECT
    sha2(customer_unique_id, 256) AS customer_key,
    customer_unique_id,
    customer_state
FROM (
    SELECT
        customer_unique_id,
        customer_state,
        row_number() OVER (
            PARTITION BY customer_unique_id
            ORDER BY order_purchase_timestamp DESC, customer_id DESC
        ) AS row_priority
    FROM olist_order_items
    WHERE customer_unique_id IS NOT NULL
)
WHERE row_priority = 1;

CREATE OR REPLACE TABLE dim_products
USING PARQUET AS
SELECT
    sha2(product_id, 256) AS product_key,
    product_id,
    coalesce(product_category_name_english, product_category_name, 'unknown') AS product_category
FROM (
    SELECT
        product_id,
        product_category_name,
        product_category_name_english,
        row_number() OVER (
            PARTITION BY product_id
            ORDER BY order_purchase_timestamp DESC
        ) AS row_priority
    FROM olist_order_items
    WHERE product_id IS NOT NULL
)
WHERE row_priority = 1;

CREATE OR REPLACE TABLE dim_sellers
USING PARQUET AS
SELECT
    sha2(seller_id, 256) AS seller_key,
    seller_id,
    seller_state
FROM (
    SELECT
        seller_id,
        seller_state,
        row_number() OVER (
            PARTITION BY seller_id
            ORDER BY order_purchase_timestamp DESC
        ) AS row_priority
    FROM olist_order_items
    WHERE seller_id IS NOT NULL
)
WHERE row_priority = 1;

CREATE OR REPLACE TABLE fact_order_items
USING PARQUET AS
SELECT
    sha2(concat_ws('|', order_id, CAST(order_item_id AS STRING)), 256) AS order_item_key,
    order_id,
    order_item_id,
    CAST(date_format(order_purchase_timestamp, 'yyyyMMdd') AS INT) AS date_key,
    sha2(customer_unique_id, 256) AS customer_key,
    sha2(product_id, 256) AS product_key,
    sha2(seller_id, 256) AS seller_key,
    order_status,
    CAST(price AS DECIMAL(14,2)) AS item_price,
    CAST(freight_value AS DECIMAL(14,2)) AS freight_value,
    CAST(item_revenue AS DECIMAL(14,2)) AS item_revenue,
    CAST(payment_total AS DECIMAL(14,2)) AS order_payment_total,
    CAST(average_review_score AS DECIMAL(4,2)) AS average_review_score,
    order_purchase_timestamp,
    current_timestamp() AS loaded_at
FROM olist_order_items;
