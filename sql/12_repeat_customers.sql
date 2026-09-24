-- =====================================================================
-- 12 - REPEAT CUSTOMERS
-- Business question: what share of customers place more than one order?
-- Optimisation: the GROUP BY finishes in SQL; an index on orders.customer_id
--               (idx_orders_customer) serves the grouping.
-- =====================================================================

WITH order_counts AS (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
)
SELECT (SELECT COUNT(*) FROM order_counts)                    AS total_customers,
       (SELECT COUNT(*) FROM order_counts WHERE order_count > 1) AS repeat_customers,
       ROUND(100.0
             * (SELECT COUNT(*) FROM order_counts WHERE order_count > 1)
             / (SELECT COUNT(*) FROM order_counts), 2)        AS repeat_rate_pct;