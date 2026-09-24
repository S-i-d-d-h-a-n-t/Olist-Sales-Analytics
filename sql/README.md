# SQL Analytics Queries

Optimised analytical queries for the **Olist E-commerce database** (`olist.db`).

## Design principles

1. **Aggregation happens in SQL** — no result set larger than the aggregation output
   is ever returned; pandas never loads whole tables.
2. **Indexes drive the lookups** — every `WHERE` / `JOIN` column used here is
   indexed by `scripts/load_data.py` (confirmed with `EXPLAIN QUERY PLAN`, see file
   comments).
3. **Parameterised and re-usable** — ready to back API endpoints or Power BI
   (Power Query / ODBC) without modification.

## How to run

```bash
# sqlite3 CLI
sqlite3 olist.db < sql/03_monthly_revenue.sql

# Or from Python
python -c "import sqlite3; print(sqlite3.connect('olist.db').execute(open('sql/03_monthly_revenue.sql').read()).fetchall())"
```

## Query index

| # | File | Business question |
|---|---|---|
| 01 | `01_top_10_selling_products.sql` | Top 10 products by units sold |
| 02 | `02_top_10_revenue_products.sql` | Top 10 products by revenue |
| 03 | `03_monthly_revenue.sql` | Revenue and orders per month |
| 04 | `04_revenue_by_state.sql` | Revenue and orders per state |
| 05 | `05_revenue_by_category.sql` | Revenue per product category |
| 06 | `06_average_order_value.sql` | Average order value (AOV) |
| 07 | `07_average_delivery_time.sql` | Average delivery time vs. estimate |
| 08 | `08_late_deliveries.sql` | Late delivery rate and severity |
| 09 | `09_top_20_customers_lifetime_value.sql` | Top 20 customers by LTV |
| 10 | `10_payment_method_distribution.sql` | Payment method mix |
| 11 | `11_cancellation_rate.sql` | Order cancellation rate |
| 12 | `12_repeat_customers.sql` | Repeat-customer share |
| 13 | `13_average_basket_size.sql` | Average items per order |
| 14 | `14_monthly_order_growth.sql` | Month-over-month order growth % |
| 15 | `15_yoy_growth.sql` | Year-over-year revenue growth % |

## Data model notes

- `payments.payment_value` is the authoritative **revenue** figure (what was paid).
- `order_items.price + freight_value` is used for **product-level** revenue.
- Orders with status `canceled` are excluded from revenue/goals.
- Customers with a missing/blank state are bucketed as `(unknown)`.