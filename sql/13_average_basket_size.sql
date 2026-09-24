-- =====================================================================
-- 13 - AVERAGE BASKET SIZE
-- Business question: on average, how many items does an order contain?
-- Optimisation: basket size computed per order in the subquery, then
--               averaged - aggregation fully pushed into SQL.
-- =====================================================================

SELECT ROUND(AVG(item_count), 2) AS avg_basket_size_items,
       COUNT(*)                  AS orders_with_items
FROM (
    SELECT order_id, COUNT(*) AS item_count
    FROM order_items
    GROUP BY order_id
);