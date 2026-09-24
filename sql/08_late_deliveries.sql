-- =====================================================================
-- 08 - LATE DELIVERIES
-- Business question: what share of deliveries arrive after the estimated
--                    date, and on average how late are they?
-- Optimisation: single pass over the pre-filtered 'delivered' set; the
--               SUM(days_late > 0) trick counts booleans in SQL.
-- =====================================================================

WITH delivered AS (
    SELECT julianday(order_delivered_customer_date)
           - julianday(order_estimated_delivery_date) AS days_late
    FROM orders
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
      AND order_estimated_delivery_date IS NOT NULL
)
SELECT COUNT(*)                                AS delivered_orders,
       SUM(days_late > 0)                       AS late_orders,
       ROUND(100.0 * SUM(days_late > 0) / COUNT(*), 2) AS late_pct,
       ROUND(AVG(days_late), 2)                 AS avg_days_late
FROM delivered;