-- User-level intent-to-treat dataset. In production, replace the local table
-- names with warehouse models while preserving one row per randomized user.
WITH exposure AS (
    SELECT
        user_id,
        MIN(assignment_date) AS assignment_date,
        MIN(treatment) AS treatment
    FROM experiment_assignments
    GROUP BY user_id
),
outcomes AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_name = 'activation' AND day_number <= 7 THEN 1 ELSE 0 END) AS activated_7d,
        MAX(CASE WHEN event_name = 'support_contact' AND day_number <= 7 THEN 1 ELSE 0 END) AS support_contact_7d,
        AVG(CASE WHEN event_name = 'transaction' THEN latency_ms END) AS transaction_latency_ms
    FROM product_events
    GROUP BY user_id
)
SELECT
    e.user_id,
    e.assignment_date,
    e.treatment,
    u.device,
    u.channel,
    u.prior_activity,
    COALESCE(o.activated_7d, 0) AS activated_7d,
    COALESCE(o.support_contact_7d, 0) AS support_contact_7d,
    o.transaction_latency_ms
FROM exposure e
JOIN users u USING (user_id)
LEFT JOIN outcomes o USING (user_id);

