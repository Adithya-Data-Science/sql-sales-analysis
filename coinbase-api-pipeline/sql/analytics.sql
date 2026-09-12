WITH daily AS (
    SELECT
        product_id,
        date(timestamp, 'unixepoch') AS trading_date,
        MIN(low) AS low_price,
        MAX(high) AS high_price,
        AVG(close) AS avg_close,
        SUM(volume) AS total_volume
    FROM candles
    GROUP BY product_id, date(timestamp, 'unixepoch')
), enriched AS (
    SELECT
        *,
        LAG(avg_close) OVER (PARTITION BY product_id ORDER BY trading_date) AS prior_avg_close
    FROM daily
)
SELECT
    product_id,
    trading_date,
    ROUND(low_price, 4) AS low_price,
    ROUND(high_price, 4) AS high_price,
    ROUND(avg_close, 4) AS avg_close,
    ROUND(total_volume, 4) AS total_volume,
    ROUND(100.0 * (avg_close / prior_avg_close - 1.0), 4) AS close_change_pct
FROM enriched
ORDER BY product_id, trading_date;
