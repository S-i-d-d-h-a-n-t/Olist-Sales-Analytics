-- =====================================================================
-- 09 - TOP 20 CUSTOMERS BY LIFETIME VALUE (LTV)
-- Business question: who are the most valuable customers, and how many
--                    orders make up that value?
-- Optimisation: customers joined on PK; revenue aggregated in SQL; only
--               the top 20 rows are ever returned.
-- =====================================================================

SELECT c.customer_unique_id,
       c.customer_city,
       c.customer_state,
       ROUND(SUM(p.payment_value), 2) AS lifetime_value,
       COUNT(DISTINCT o.order_id)      AS order_count
FROM payments AS p
JOIN orders    AS o ON o.order_id = p.order_id
JOIN customers AS c ON c.customer_id = o.customer_id
WHERE o.order_status != 'canceled'
GROUP BY c.customer_unique_id
ORDER BY lifetime_value DESC
LIMIT 20;