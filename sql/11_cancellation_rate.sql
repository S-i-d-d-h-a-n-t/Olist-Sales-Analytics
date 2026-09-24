-- =====================================================================
-- 11 - CANCELLATION RATE
-- Business question: what share of orders end up canceled?
-- Optimisation: single table scan, scalar aggregates only.
-- =====================================================================

SELECT COUNT(*) AS total_orders,
       SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END) AS canceled_orders,
       ROUND(100.0
             * SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END)
             / COUNT(*), 2) AS cancellation_rate_pct
FROM orders;