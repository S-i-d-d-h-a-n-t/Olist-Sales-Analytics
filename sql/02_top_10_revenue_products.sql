-- =====================================================================
-- 02 - TOP 10 REVENUE GENERATING PRODUCTS
-- Business question: which products drive the most revenue?
-- Optimisation: product-level revenue is aggregated in SQL from
--               order_items (price + freight), no row is shipped to app.
-- =====================================================================

SELECT p.product_id,
       p.product_category_name,
       ROUND(SUM(oi.price + oi.freight_value), 2) AS revenue
FROM order_items AS oi
JOIN products     AS p ON p.product_id = oi.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;