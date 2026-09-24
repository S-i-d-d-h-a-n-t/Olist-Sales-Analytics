# Olist E-commerce API — Project Documentation

Complete documentation for the Olist E-commerce API project.

| | |
|---|---|
| **Application** | Olist E-commerce API |
| **Stack** | Python · FastAPI · SQLite · Pandas |
| **Version** | 2.3 |
| **Dataset** | Olist E-commerce (9 CSV files → SQLite) |
| **Dashboard** | Power BI (`Power BI Dashboard.pbix`) |

---

## Table of Contents

1. [Overview](#1-overview)
2. [Repository Structure](#2-repository-structure)
3. [Installation](#3-installation)
4. [Dependencies](#4-dependencies)
5. [Database & Data Model](#5-database--data-model)
6. [Running the API](#6-running-the-api)
7. [Authentication](#7-authentication)
8. [API Endpoints](#8-api-endpoints)
9. [SQL Analytics](#9-sql-analytics)
10. [Dashboard (Power BI)](#10-dashboard-power-bi)
11. [Testing](#11-testing)
12. [Assumptions](#12-assumptions)
13. [Known Limitations](#13-known-limitations)
14. [Version History](#14-version-history)

---

## 1. Overview

This repository contains the **Olist E-commerce analytical solution**. It includes:

- a **relational SQLite database** (`olist.db`) with primary keys, enforced foreign keys and indexes;
- a **REST API** built with FastAPI exposing Products, Customers, Orders and Categories;
- **15 optimised SQL analytics queries** in `sql/` with all aggregation pushed down to the database;
- a **Power BI dashboard** file;
- a **process log** — see `DEVELOPMENT_PROCESS.md` for the full build history (Phases 1–4).

---

## 2. Repository Structure

```
olist-api/
├── api/                        # FastAPI application (modular package)
│   ├── __init__.py
│   ├── main.py                 # entry point — assembles the routers
│   ├── config.py               # all settings/constants
│   ├── database.py             # db connection context manager + response shaping
│   ├── security.py             # x-api-key authentication dependency
│   ├── crud.py                 # all SQL / data-access helpers
│   └── routers/
│       ├── __init__.py
│       ├── products.py         # GET /products, /products/{id}
│       ├── customers.py        # GET /customers, /customers/{id}
│       ├── orders.py           # GET /orders, /orders/{id}, /orders/{id}/details
│       ├── categories.py       # GET /categories, /categories/translation
│       └── catalog.py          # backwards-compatible tables
├── scripts/
│   └── load_data.py            # CSV → SQLite loader (PKs, FKs, indexes)
├── sql/                        # 15 optimised analytics queries + README
│   ├── README.md
│   └── 01_...sql … 15_yoy_growth.sql
├── data/                       # 9 source CSV files (Olist dataset)
├── olist.db                    # generated SQLite database (~189 MB)
├── tests/                      # pytest test suite (see §11)
├── Power BI Dashboard.pbix     # Power BI dashboard
├── DEVELOPMENT_PROCESS.md      # full development history (Phases 1–4)
├── README.md                   # quick-start readme
├── requirements.txt
└── back2.jpg / grabient-*.png  # dashboard theme assets
```

---

## 3. Installation

### 3.1 Prerequisites

- **Python 3.10+** (developed and verified on 3.12.2)
- **pip** (comes with Python)
- SQLite is included in the Python standard library — no extra install needed.

### 3.2 Steps

```bash
# 1. (Recommended) create and activate a virtual environment
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build the database from the CSVs (creates olist.db with PK/FKs/indexes)
python scripts/load_data.py

# 4. Start the API
uvicorn api.main:app --reload
```

### 3.3 Verify

- Open **http://127.0.0.1:8000/docs** — you should see the interactive Swagger UI with all endpoints.
- Call the health/home endpoint: http://127.0.0.1:8000/ (no auth needed).

---

## 4. Dependencies

Declared in `requirements.txt`:

| Package | Pinned version | Purpose |
|---|---|---|
| `fastapi` | `==0.116.1` | Web framework |
| `uvicorn` | `==0.51.0` | ASGI server |
| `pandas` | `==2.1.1` | CSV reading in the loader, SQL result shaping |
| `numpy` | `==1.26.0` | Numeric support for pandas |

**Implicit (installed with fastapi):** `pydantic` (validation), `starlette`, `httpx` (used only by the test client), `typing-extensions`, `anyio`.

> **Note:** the API was developed and verified against fastapi 0.115.5 / uvicorn 0.32.1 / pandas 2.3.2; the pins in `requirements.txt` are compatible. SQLite is used via the stdlib `sqlite3` module.

## 5. Database & Data Model

`scripts/load_data.py` reads the 9 CSVs in `data/` and produces `olist.db` with a proper relational schema — tables with **primary keys**, **enforced foreign keys** (`PRAGMA foreign_keys = ON`) and **13 indexes** on every join/lookup column.

| Table | Rows | Primary key | Notes |
|---|---|---|---|
| `category_translation` | 71 | `product_category_name` | Spanish → English category names |
| `customers` | 99,441 | `customer_id` | Unique customer id, zip prefix, city, state |
| `products` | 32,951 | `product_id` | Category, weight/dimensions, photo count |
| `sellers` | 3,095 | `seller_id` | Zip prefix, city, state |
| `orders` | 99,441 | `order_id` | Status, purchase/approval/delivery timestamps |
| `order_items` | 112,650 | `(order_id, order_item_id)` | Product/seller per order line, price, freight |
| `payments` | 103,886 | `(order_id, payment_sequential)` | Payment type, installments, value |
| `reviews` | 99,224 | `(review_id, order_id)` | Score 1–5, comment, dates |
| `geolocation` | 1,000,163 | *(none)* | Zip-prefix coordinates; 1M rows share zips → indexed, not a key |

**Data integrity decisions**

- Zip-code prefixes are stored as **text** (`01003`), preserving leading zeros so geographic joins against `geolocation` work.
- Every foreign key is verified with **zero orphan rows** (`PRAGMA foreign_key_check`).
- `products.product_category_name` is deliberately **not** a foreign key to `category_translation` (2 categories / 623 products exist in products but not in the translation file — enforced FK would drop data).
- `geolocation` has no natural key (duplicate zip prefixes), so it gets indexes on `geolocation_zip_code_prefix` and `geolocation_state`.

---

## 6. Running the API

```bash
uvicorn api.main:app --reload
```

- Base URL: `http://127.0.0.1:8000`
- Interactive docs (Swagger): `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Rebuild the database anytime with: `python scripts/load_data.py`

---

## 7. Authentication

Every endpoint **except `GET /`** requires an API key in the `x-api-key` header:

```
x-api-key: olist-api-2026
```

| Scenario | HTTP status |
|---|---|
| Missing header | `401 Invalid API Key` |
| Wrong key | `401 Invalid API Key` |
| Valid key | proceeds to the endpoint |

In the Swagger UI (`/docs`), click **Authorize** and enter `olist-api-2026` once.

```bash
# Example
curl -H "x-api-key: olist-api-2026" "http://127.0.0.1:8000/products?page=1&limit=5"
```

## 8. API Endpoints

All endpoints are `GET`. List endpoints return a standard **pagination envelope**; single-record endpoints return the row object directly.

### 8.1 Pagination envelope (list endpoints)

```json
{
  "page": 1,
  "limit": 100,
  "total_records": 32951,
  "returned_records": 100,
  "has_next": true,
  "data": [ { "…row…" } ]
}
```

| Field | Meaning |
|---|---|
| `page` / `limit` | requested page (≥ 1) and page size (1–1000) |
| `total_records` | total rows available across all pages |
| `returned_records` | rows in this response |
| `has_next` | whether another page exists |
| `data` | array of row objects (`NaN` encoded as `null`) |

**Query parameters** (list endpoints): `page` (default `1`, must be ≥ 1), `limit` (default `100`, 1–1000). Invalid values → `422`.

### 8.2 Products

| Method | Path | Auth | Paginated | Description |
|---|---|---|---|---|
| GET | `/products` | ✅ | ✅ | List products |
| GET | `/products/{product_id}` | ✅ | — | Single product by id |

Example — single product:

```json
{
  "product_id": "1e9e8ef04dbcff4541ed26657ea517e5",
  "product_category_name": "perfumaria",
  "product_name_lenght": 40,
  "product_description_lenght": 287,
  "product_photos_qty": 1,
  "product_weight_g": 225,
  "product_length_cm": 16,
  "product_height_cm": 10,
  "product_width_cm": 14
}
```

### 8.3 Customers

| Method | Path | Auth | Paginated | Description |
|---|---|---|---|---|
| GET | `/customers` | ✅ | ✅ | List customers |
| GET | `/customers/{customer_id}` | ✅ | — | Single customer by id |

### 8.4 Orders

| Method | Path | Auth | Paginated | Description |
|---|---|---|---|---|
| GET | `/orders` | ✅ | ✅ | List orders |
| GET | `/orders/{order_id}` | ✅ | — | Single order by id |
| GET | `/orders/{order_id}/details` | ✅ | — | Order plus nested `items`, `payments`, `reviews` |

Example — order details response shape:

```json
{
  "order":    { "order_id": "…", "customer_id": "…", "order_status": "delivered", "…" },
  "items":    [ { "order_id": "…", "order_item_id": 1, "product_id": "…", "price": 58.9, "…" } ],
  "payments": [ { "order_id": "…", "payment_sequential": 1, "payment_type": "credit_card", "…" } ],
  "reviews":  [ { "review_id": "…", "review_score": 4, "…" } ]
}
```

### 8.5 Categories

| Method | Path | Auth | Paginated | Description |
|---|---|---|---|---|
| GET | `/categories` | ✅ | ✅ | Distinct product categories ranked by product count |
| GET | `/categories/translation` | ✅ | ✅ | Category translation table (Spanish → English) |

Example — `/categories` row: `{"category": "cama_mesa_banho", "product_count": 3029}`. Products with a blank/`NULL` category are bucketed as `"(unknown)"`.

### 8.6 Additional catalog tables (backwards-compatible)

| Method | Path | Auth | Paginated |
|---|---|---|---|
| GET | `/order_items` | ✅ | ✅ |
| GET | `/payments` | ✅ | ✅ |
| GET | `/sellers` | ✅ | ✅ |
| GET | `/reviews` | ✅ | ✅ |
| GET | `/geolocation` | ✅ | ✅ |
| GET | `/category_translation` | ✅ | ✅ |

### 8.7 Home

`GET /` — welcome message and version (no authentication).

### 8.8 Error responses

| Status | Meaning | Example body |
|---|---|---|
| `401` | missing/invalid `x-api-key` | `{"detail": "Invalid API Key"}` |
| `404` | resource not found | `{"detail": "Record not found in 'products' with product_id = 'nonexistent'"}` |
| `422` | invalid `page`/`limit` | FastAPI validation detail (e.g. `"Input should be greater than or equal to 1"`) |
| `500` | database missing or internal failure | message includes the setup hint (`Run 'python scripts/load_data.py'`) |

## 9. SQL Analytics

The `sql/` folder contains **15 read-optimised analytics queries**: aggregation is performed entirely in SQL (the largest result set is 74 rows), and every join / filter column is indexed.

| # | File | Business question |
|---|---|---|
| 01 | `01_top_10_selling_products.sql` | Top 10 products by units sold |
| 02 | `02_top_10_revenue_products.sql` | Top 10 products by revenue |
| 03 | `03_monthly_revenue.sql` | Revenue and order volume per month |
| 04 | `04_revenue_by_state.sql` | Revenue and orders per state |
| 05 | `05_revenue_by_category.sql` | Revenue per product category |
| 06 | `06_average_order_value.sql` | Average order value (AOV) |
| 07 | `07_average_delivery_time.sql` | Avg delivery time vs. estimate |
| 08 | `08_late_deliveries.sql` | Late delivery rate and severity |
| 09 | `09_top_20_customers_lifetime_value.sql` | Top 20 customers by LTV |
| 10 | `10_payment_method_distribution.sql` | Payment method mix |
| 11 | `11_cancellation_rate.sql` | Order cancellation rate |
| 12 | `12_repeat_customers.sql` | Repeat-customer share |
| 13 | `13_average_basket_size.sql` | Average basket size |
| 14 | `14_monthly_order_growth.sql` | Month-over-month order growth % |
| 15 | `15_yoy_growth.sql` | Year-over-year revenue growth % |

**How to run a query.**

```bash
# sqlite3 CLI
sqlite3 olist.db < sql/03_monthly_revenue.sql

# Python
python -c "import sqlite3; c = sqlite3.connect('olist.db'); print(c.execute(open('sql/03_monthly_revenue.sql').read()).fetchall())"
```

**Sample verified results** (from the current `olist.db`):

| Metric | Value |
|---|---|
| Average order value (AOV) | **€160.56** over 98,815 non-canceled orders |
| Total tracked revenue | **€15,865,616.52** |
| Late deliveries | **8.11 %** (7,826 of 96,470 delivered orders) |
| Payment mix leader | **credit_card — 73.9 %** |
| Top category by product count | `cama_mesa_banho` (3,029 products) |

---

## 10. Dashboard (Power BI)

The Power BI dashboard is provided as **`Power BI Dashboard.pbix`** at the repository root. It is designed around the same `olist.db` built by `scripts/load_data.py` (connect Power BI to the SQLite file directly, or export the `sql/` queries via Power Query / ODBC).

**Included visual assets** (repository root, for the dashboard theme):

![Dashboard logo and theme asset](./grabient-_gLqgLqgPhf83gBk.png)

![Dashboard theme background](./back2.jpg)

### Dashboard screenshots

> 📸 **To complete:** capture screenshots of the open dashboard and add them below
> (Power BI: *View → Full screen* or *Export → PNG/PDF*, then drop the files into the
> repo and reference them here). Suggested placeholders:

```markdown
![Dashboard — Executive KPIs](./screenshots/kpi_overview.png)
![Dashboard — Revenue trend & geo map](./screenshots/trends.png)
![Dashboard — Products, customers & delivery](./screenshots/details.png)
```

**Recommended dashboard content:** executive KPI cards (Revenue, Orders, Customers, AOV), top categories, monthly revenue trend, revenue by state (map), payment method distribution, order status distribution, top products, top customers, delivery performance, with interactive filters for date / state / category / payment type.

## 11. Testing

### 11.1 Quick endpoint check (Python)

```python
import requests

BASE, KEY = "http://127.0.0.1:8000", {"x-api-key": "olist-api-2026"}

# list + pagination
r = requests.get(f"{BASE}/products", params={"page": 1, "limit": 5}, headers=KEY)
print(r.status_code, r.json()["total_records"], r.json()["has_next"])

# single record / nested details
print(requests.get(f"{BASE}/products/{'1e9e8ef04dbcff4541ed26657ea517e5'}", headers=KEY).status_code)
print(requests.get(f"{BASE}/orders/{'e481f51cbdc54678b7cc49136f2d6af7'}/details", headers=KEY).json().keys())

# categories
print(requests.get(f"{BASE}/categories", headers=KEY).json()["data"][0])

# error paths
print(requests.get(f"{BASE}/products").status_code)                        # 401
print(requests.get(f"{BASE}/products/zzz", headers=KEY).status_code)       # 404
print(requests.get(f"{BASE}/products", params={"page": 0}, headers=KEY).status_code)  # 422
```

### 11.2 Automated test suite

A pytest suite lives in **`tests/test_api.py`** — run it from the project root:

```bash
python -m pytest tests -v
```

It exercises every endpoint, all auth (`401`), missing-record (`404`), pagination-envelope and input-validation (`422`) paths, plus the backward-compatible tables. Latest run: **27 passed**.

> Functional verification history (including the 38-check smoke runs and live uvicorn boots) is recorded in `DEVELOPMENT_PROCESS.md` §8.

---

## 12. Assumptions

1. **IDs are text primary keys** — `order_id`, `customer_id`, `product_id` are 32-character hex strings; the schema declares them `TEXT PRIMARY KEY`.
2. **Category semantics** — products with a blank/`NULL` `product_category_name` are reported as `(unknown)` in `/categories` and analytics, never dropped.
3. **Revenue definitions** — `payments.payment_value` is the authoritative revenue figure; `order_items.price + freight_value` is used for product-level revenue; canceled orders are excluded from revenue metrics.
4. **Backwards compatibility** — the pre-existing generic table endpoints (`/order_items`, `/payments`, `/sellers`, `/reviews`, `/geolocation`, `/category_translation`) are preserved alongside the required endpoints.
5. **API key location** — `olist-api-2026` lives in `api/config.py` for demonstration convenience; a production deployment should read it from an environment variable.
6. **Source column names kept** — misspellings from the source CSV (`product_name_lenght`) are deliberately preserved so `SELECT *` responses match the source schema.
7. **Review identity** — `review_id` is not unique in the raw data, so `reviews` uses the composite key `(review_id, order_id)`.

---

## 13. Known Limitations

| # | Limitation | Status |
|---|---|---|
| 1 | `products.product_category_name → category_translation` is **not** an enforced FK — 2 categories / 623 products exist in `products` but not in the translation file (enforcing it would silently drop data). | documented exception |
| 2 | The **advanced analytics metrics exist as SQL** (`sql/`) but are **not yet exposed as HTTP endpoints** — the queries are written and verified, the endpoints are the remaining work. | planned |
| 3 | API key is hardcoded in `api/config.py` (see Assumption 5). | accepted for this deployment |
| 4 | Dashboard screenshots are not yet captured into the repo (placeholders provided in §10). | to complete |
| 5 | Repository `README.md` still reflects the original v2.1 API surface; this file (`PROJECT_DOCUMENTATION.md`) is the authoritative documentation. | superseded by this doc |
| 6 | The database is regenerated as a whole (`python scripts/load_data.py`); there is no incremental/CDC load path. | design choice |

---

## 14. Version History

| Version | Change |
|---|---|
| **2.1** | Original scaffold: single `api/main.py`, 11 routes, generic paginated table loader. |
| **2.2** | Added `/products/{id}`, `/customers/{id}`, `/orders/{id}`, `/categories`, `/categories/translation`; input validation, parameterized SQL, allow-listed tables, safer error handling. |
| **2.3** | Refactored into a modular package (`config/database/security/crud/routers`); auth as a reusable FastAPI dependency (OpenAPI `Authorize` button). |
| **—** | `scripts/load_data.py` now builds a relational schema (PKs, enforced FKs, 13 indexes); `sql/` added with 15 optimised analytics queries; zip-prefix data-corruption bug fixed. |

---

*End of project documentation. See `DEVELOPMENT_PROCESS.md` for the full build log and verification evidence.*