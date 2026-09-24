-- =====================================================================
-- 07 - AVERAGE DELIVERY TIME
-- Business question: how long does delivery take, and how does reality
--                    compare with the estimated date?
-- Definitions (days as floating-point using julianday):
--   actual time   = delivered to customer  -  purchase timestamp
--   vs. estimate  = delivered to customer  -  estimated delivery date
-- Optimisation: filtered to 'delivered' orders only; NULL dates excluded.
-- =====================================================================

SELECT ROUND(AVG(
           julianday(order_delivered_customer_date)
           - julianday(order_purchase_timestamp)), 2)      AS avg_delivery_days_from_purchase,
       ROUND(AVG(
           julianday(order_delivered_customer_date)
           - julianday(order_estimated_delivery_date)), 2) AS avg_days_vs_estimate,
       COUNT(*)                                             AS delivered_with_dates
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL
  AND order_purchase_timestamp IS NOT NULL;