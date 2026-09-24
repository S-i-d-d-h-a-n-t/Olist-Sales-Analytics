-- =====================================================================
-- 10 - PAYMENT METHOD DISTRIBUTION
-- Business question: which payment methods are used, by count, value
--                    and share?
-- Optimisation: window function (SUM() OVER) computes the total in SQL;
--               only 4-5 aggregated rows leave the database.
-- =====================================================================

SELECT payment_type,
       COUNT(*)                        AS payment_count,
       ROUND(SUM(payment_value), 2)    AS total_value,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_payments
FROM payments
GROUP BY payment_type
ORDER BY payment_count DESC;