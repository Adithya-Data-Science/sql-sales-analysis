-- Executable warehouse assertions for Spark SQL.
-- Every query must return zero rows. A returned row is a failed test.

-- 1. Fact-table grain is unique.
SELECT order_id, order_item_id, COUNT(*) AS duplicate_count
FROM fact_order_items
GROUP BY order_id, order_item_id
HAVING COUNT(*) > 1;

-- 2. Required identifiers and measures are present and valid.
SELECT order_item_key
FROM fact_order_items
WHERE order_id IS NULL
   OR order_item_id IS NULL
   OR date_key IS NULL
   OR customer_key IS NULL
   OR product_key IS NULL
   OR seller_key IS NULL
   OR item_price < 0
   OR freight_value < 0;

-- 3. Every fact customer resolves to its dimension.
SELECT f.customer_key
FROM fact_order_items f
LEFT JOIN dim_customers d ON f.customer_key = d.customer_key
WHERE d.customer_key IS NULL
GROUP BY f.customer_key;

-- 4. Every fact product resolves to its dimension.
SELECT f.product_key
FROM fact_order_items f
LEFT JOIN dim_products d ON f.product_key = d.product_key
WHERE d.product_key IS NULL
GROUP BY f.product_key;

-- 5. Every fact seller resolves to its dimension.
SELECT f.seller_key
FROM fact_order_items f
LEFT JOIN dim_sellers d ON f.seller_key = d.seller_key
WHERE d.seller_key IS NULL
GROUP BY f.seller_key;

-- 6. Every fact date resolves to its dimension.
SELECT f.date_key
FROM fact_order_items f
LEFT JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date_key IS NULL
GROUP BY f.date_key;

-- 7. Item revenue reconciles to price plus freight within one cent.
SELECT order_item_key
FROM fact_order_items
WHERE ABS(item_revenue - (item_price + freight_value)) > 0.01;

-- 8. Review score remains inside the documented Olist scale.
SELECT order_item_key
FROM fact_order_items
WHERE average_review_score IS NOT NULL
  AND (average_review_score < 1 OR average_review_score > 5);
