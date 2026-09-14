-- BI-ready examples
SELECT c.state, COUNT(*) AS orders, ROUND(SUM(f.amount), 2) AS revenue
FROM fact_orders f
JOIN dim_customers c USING(customer_key)
WHERE f.status = 'completed'
GROUP BY c.state
ORDER BY revenue DESC;

SELECT c.customer_id, c.customer_name, ROUND(SUM(f.amount), 2) AS lifetime_value
FROM fact_orders f
JOIN dim_customers c USING(customer_key)
GROUP BY c.customer_id, c.customer_name
ORDER BY lifetime_value DESC;
