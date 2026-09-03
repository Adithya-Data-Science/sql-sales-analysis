-- Monthly delivered-order KPIs from the validated Parquet output.
SELECT
    date_trunc('month', order_purchase_timestamp) AS purchase_month,
    customer_state,
    COUNT(DISTINCT order_id) AS delivered_orders,
    ROUND(SUM(item_revenue), 2) AS gross_item_value,
    ROUND(AVG(average_review_score), 2) AS average_review_score
FROM olist_order_items
WHERE order_status = 'delivered'
GROUP BY date_trunc('month', order_purchase_timestamp), customer_state
ORDER BY purchase_month, customer_state;

-- Validate payment totals against item and freight totals at order grain.
WITH order_totals AS (
    SELECT
        order_id,
        ROUND(SUM(item_revenue), 2) AS item_and_freight_total,
        MAX(payment_total) AS payment_total
    FROM olist_order_items
    GROUP BY order_id
)
SELECT
    COUNT(*) AS compared_orders,
    SUM(CASE WHEN ABS(item_and_freight_total - payment_total) > 0.01 THEN 1 ELSE 0 END) AS mismatched_orders
FROM order_totals
WHERE payment_total IS NOT NULL;
