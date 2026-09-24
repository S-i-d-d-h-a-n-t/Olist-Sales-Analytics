-- =====================================================================
-- 04 - REVENUE BY STATE
-- Business question: which states generate the most revenue / orders?
-- Optimisation: joins ride the customers PK + indexes; LEFT JOIN keeps
--               orders whose customer state is unknown (bucketed below).
-- =====================================================================

SELECT COALESCE(NULLIF(c.customer_state, ''), '(unknown)') AS state,
       ROUND(SUM(p.payment_value), 2)                      AS revenue,
       COUNT(DISTINCT o.order_id)                           AS order_count
FROM payments AS p
JOIN orders    AS o ON o.order_id = p.order_id
LEFT JOIN customers AS c ON c.customer_id = o.customer_id
WHERE o.order_status != 'canceled'
GROUP BY state
ORDER BY revenue DESC;