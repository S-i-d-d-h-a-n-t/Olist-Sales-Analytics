-- =====================================================================
-- 06 - AVERAGE ORDER VALUE (AOV)
-- Business question: how much does the average (non-canceled) order bring?
-- Optimisation: two scalar aggregates, zero row data transferred.
-- =====================================================================

SELECT ROUND(SUM(p.payment_value) / COUNT(DISTINCT p.order_id), 2) AS average_order_value,
       ROUND(SUM(p.payment_value), 2)                             AS total_revenue,
       COUNT(DISTINCT p.order_id)                                 AS order_count
FROM payments AS p
JOIN orders AS o ON o.order_id = p.order_id
WHERE o.order_status != 'canceled';