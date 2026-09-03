-- Customer growth and sales-operations analysis for the Olist dataset.
-- Designed for Spark SQL after the validated order-items pipeline is loaded
-- as the olist_order_items view.

WITH customer_orders AS (
    SELECT
        customer_unique_id,
        customer_state,
        COUNT(DISTINCT order_id) AS order_count,
        ROUND(SUM(item_revenue), 2) AS lifetime_value,
        ROUND(AVG(average_review_score), 2) AS average_review_score,
        MAX(order_purchase_timestamp) AS most_recent_purchase
    FROM olist_order_items
    WHERE order_status = 'delivered'
    GROUP BY customer_unique_id, customer_state
),
scored AS (
    SELECT
        *,
        NTILE(4) OVER (ORDER BY lifetime_value DESC) AS value_quartile,
        DATEDIFF(MAX(most_recent_purchase) OVER (), most_recent_purchase) AS recency_days
    FROM customer_orders
)
SELECT
    customer_state,
    COUNT(*) AS customers,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 2)
        AS repeat_customer_rate,
    ROUND(AVG(lifetime_value), 2) AS average_customer_value,
    SUM(CASE WHEN value_quartile = 1 AND recency_days <= 90 THEN 1 ELSE 0 END)
        AS high_value_recent_customers,
    SUM(CASE WHEN value_quartile = 1 AND recency_days > 90 THEN 1 ELSE 0 END)
        AS high_value_reengagement_candidates,
    ROUND(AVG(average_review_score), 2) AS average_review_score
FROM scored
GROUP BY customer_state
ORDER BY average_customer_value DESC;

-- Salesforce-ready outreach queue. The public dataset contains no email or
-- phone fields, so the output uses customer IDs and avoids invented contacts.
WITH customer_summary AS (
    SELECT
        customer_unique_id,
        customer_state,
        COUNT(DISTINCT order_id) AS order_count,
        ROUND(SUM(item_revenue), 2) AS lifetime_value,
        ROUND(AVG(average_review_score), 2) AS average_review_score,
        MAX(order_purchase_timestamp) AS most_recent_purchase
    FROM olist_order_items
    WHERE order_status = 'delivered'
    GROUP BY customer_unique_id, customer_state
)
SELECT
    customer_unique_id AS external_customer_id,
    customer_state AS market_region,
    order_count,
    lifetime_value,
    average_review_score,
    most_recent_purchase,
    CASE
        WHEN order_count > 1 AND average_review_score >= 4 THEN 'Loyal customer'
        WHEN lifetime_value >= 500 AND average_review_score >= 4 THEN 'High-value prospect'
        WHEN average_review_score <= 2 THEN 'Service recovery'
        ELSE 'Standard nurture'
    END AS outreach_segment
FROM customer_summary
ORDER BY lifetime_value DESC;
