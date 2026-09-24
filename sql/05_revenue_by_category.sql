-- =====================================================================
-- 05 - REVENUE BY CATEGORY
-- Business question: which product categories earn the most revenue?
-- Note: product category is the raw Spanish name; join it to
--       category_translation when English labels are needed.
-- =====================================================================

SELECT COALESCE(NULLIF(p.product_category_name, ''), '(unknown)') AS category,
       ROUND(SUM(oi.price + oi.freight_value), 2)                AS revenue,
       COUNT(*)                                                   AS items_sold
FROM order_items AS oi
JOIN products     AS p ON p.product_id = oi.product_id
GROUP BY category
ORDER BY revenue DESC;