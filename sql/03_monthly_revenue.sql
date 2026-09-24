-- =====================================================================
-- 03 - MONTHLY REVENUE
-- Business question: how does revenue and order volume trend by month?
-- Revenue = payments.payment_value (actual amount paid).
-- Optimisation: payments joined to orders on the indexed order PK;
--               aggregation fully in SQL (returns ~50 rows, not 100k+).
-- =====================================================================

SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS month,
       ROUND(SUM(p.payment_value), 2)                AS revenue,
       COUNT(DISTINCT o.order_id)                     AS order_count
FROM payments AS p
JOIN orders   AS o ON o.order_id = p.order_id
WHERE o.order_status != 'canceled'
  AND o.order_purchase_timestamp IS NOT NULL
GROUP BY month
ORDER BY month;