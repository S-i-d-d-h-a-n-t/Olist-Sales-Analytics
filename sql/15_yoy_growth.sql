-- =====================================================================
-- 15 - YEAR-OVER-YEAR GROWTH
-- Business question: does the business grow compared with the same time
--                    last year? (Revenue-based, using paid amounts.)
-- Optimisation: yearly revenue aggregated in SQL, LAG() computes the
--               previous year; only ~4 rows leave the database.
-- =====================================================================

WITH yearly AS (
    SELECT CAST(strftime('%Y', o.order_purchase_timestamp) AS INTEGER) AS year,
           SUM(p.payment_value)                                       AS revenue
    FROM payments AS p
    JOIN orders   AS o ON o.order_id = p.order_id
    WHERE o.order_purchase_timestamp IS NOT NULL
      AND o.order_status != 'canceled'
    GROUP BY year
)
SELECT year,
       ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year))
             / LAG(revenue) OVER (ORDER BY year), 2) AS yoy_growth_pct
FROM yearly
ORDER BY year;