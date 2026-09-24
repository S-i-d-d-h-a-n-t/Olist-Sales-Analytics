-- =====================================================================
-- 14 - MONTHLY ORDER GROWTH %
-- Business question: how does order volume grow month over month?
-- Optimisation: LAG() window function computes the previous month inside
--               SQL; only one row per month leaves the database.
-- =====================================================================

WITH monthly AS (
    SELECT strftime('%Y-%m', order_purchase_timestamp) AS month,
           COUNT(*)                                   AS order_count
    FROM orders
    WHERE order_purchase_timestamp IS NOT NULL
    GROUP BY month
)
SELECT month,
       order_count,
       ROUND(100.0 * (order_count - LAG(order_count) OVER (ORDER BY month))
             / LAG(order_count) OVER (ORDER BY month), 2) AS growth_pct
FROM monthly
ORDER BY month;