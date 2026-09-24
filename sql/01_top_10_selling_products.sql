-- =====================================================================
-- 01 - TOP 10 SELLING PRODUCTS
-- Business question: which products sell the most units?
-- Optimisation: single indexed GROUP BY over order_items.product_id
--               (uses idx_items_product); products joined only for names.
-- =====================================================================

SELECT p.product_id,
       p.product_category_name,
       COUNT(*) AS units_sold
FROM order_items AS oi
JOIN products   AS p ON p.product_id = oi.product_id
GROUP BY p.product_id
ORDER BY units_sold DESC
LIMIT 10;