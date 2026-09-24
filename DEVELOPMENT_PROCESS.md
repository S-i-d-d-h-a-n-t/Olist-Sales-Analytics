# Development Process Documentation

**Project:** Olist E-commerce API
**Document:** Records the complete development process up to this point: analysis → implementation → refactor → verification.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Environment](#2-environment)
3. [Project Structure](#3-project-structure)
4. [Phase 1 — Read & Analyze `api/` and `scripts/`](#4-phase-1--read--analyze-api-and-scripts)
5. [Phase 2 — Build the FastAPI Application](#5-phase-2--build-the-fastapi-application)
6. [Phase 3 — Code Quality Refactor](#6-phase-3--code-quality-refactor)
7. [Phase 4 — SQL Layer](#7-phase-4--sql-layer)
8. [Verification & Test Results](#8-verification--test-results)
9. [How to Run the Project](#9-how-to-run-the-project)
10. [Assumptions & Known Limitations](#10-assumptions--known-limitations)
11. [Next Steps](#11-next-steps)

---

## 1. Overview

This log records how the **Olist E-commerce analytical solution** was built. The solution targets:

- **Database**: CSVs loaded into SQLite with meaningful names, correct types, primary/foreign keys
- **REST API**: FastAPI application with Products, Customers, Orders and Categories endpoints (pagination where applicable)
- **Advanced Analytics**: analytical queries (top products, revenue, delivery, LTV, …)
- **SQL**: optimized SQL with aggregation pushed down to the database
- **Dashboard**: Power BI / Tableau dashboard
- **Code Quality**: error handling, input validation, meaningful names, comments, modular code, reusable functions
- **Documentation**: README, installation, endpoints, assumptions, limitations

**Work completed to date:** REST API, code-quality refactor and the SQL layer (relational schema + optimised queries). The schema work is delivered through the loader; analytics endpoints, dashboard refresh and the documentation refresh remain pending (see [§11](#11-next-steps)).

---

## 2. Environment

| Item | Value |
|---|---|
| OS | Windows (win32) — PowerShell 7 shell |
| Python | 3.12.2 |
| pip | 26.0.1 |
| fastapi | 0.115.5 installed (`requirements.txt` pins `==0.116.1`) |
| uvicorn | 0.32.1 installed (pinned `==0.51.0`) |
| pandas | 2.3.2 installed (pinned `==2.1.1`) |
| numpy | 1.26.0 |
| httpx | 0.28.1 (used by FastAPI `TestClient`) |
| pydantic | 2.10.3 |
| SQLite | stdlib `sqlite3` |
| Database | `olist.db` — **189.12 MB**, generated from the CSVs with PK/FK/indexes |

> **Note:** installed versions differ slightly from `requirements.txt` pins; the application is verified working on the installed versions above.

---

## 3. Project Structure

```
olist-api/
├── api/                        # FastAPI application (modular package)
│   ├── __init__.py
│   ├── main.py                 # entry point — assembles routers
│   ├── config.py               # all settings/constants
│   ├── database.py             # db connection context-manager + response shaping
│   ├── security.py             # x-api-key authentication dependency
│   ├── crud.py                 # all SQL / data-access helpers
│   └── routers/
│       ├── __init__.py
│       ├── products.py         # GET /products, /products/{id}
│       ├── customers.py        # GET /customers, /customers/{id}
│       ├── orders.py           # GET /orders, /orders/{id}, /orders/{id}/details
│       ├── categories.py       # GET /categories, /categories/translation
│       └── catalog.py          # backwards-compatible tables
├── data/                       # 9 source CSVs (Olist dataset)
├── sql/                        # 15 optimised analytics queries (Part 4 deliverable)
│   ├── README.md
│   ├── 01_top_10_selling_products.sql … 15_yoy_growth.sql
├── scripts/
│   └── load_data.py            # CSV -> SQLite loader (PKs, FKs, indexes)
├── olist.db                    # generated SQLite database (189.12 MB)
├── Power BI Dashboard.pbix     # dashboard file (pre-existing)
├── README.md
├── requirements.txt
└── Business Questions.txt
```

**Database tables** (created by `scripts/load_data.py`): `customers`, `orders`, `order_items`, `payments`, `products`, `sellers`, `reviews`, `geolocation`, `category_translation`.

---

## 4. Phase 1 — Read & Analyze `api/` and `scripts/`

### 4.1 What existed before this work

| File | Lines | Purpose |
|---|---|---|
| `api/main.py` | 291 | Original FastAPI app (v2.1): 11 endpoints, `x-api-key` auth, generic paginated table loader |
| `scripts/load_data.py` | 33 | Loads all 9 CSVs into SQLite via `pandas.to_sql` |

Original endpoints: `/`, `/customers`, `/orders`, `/order_items`, `/payments`, `/products`, `/sellers`, `/reviews`, `/geolocation`, `/category_translation`, `/orders/{order_id}/details`.

### 4.2 Initial gap analysis

| Requirement | Status in original code |
|---|---|
| `GET /products`, `/customers`, `/orders` (paginated) | ✅ present |
| `GET /products/{id}`, `/customers/{id}`, `/orders/{id}` | ❌ **missing** |
| `GET /categories`, `GET /categories/translation` | ❌ **missing** (only `/category_translation`) |
| `GET /orders/{id}/details` | ✅ present |
| Advanced analytics endpoints (15) | ❌ entirely missing |
| Primary/foreign keys | ❌ tables created without PK/FK |
| Code quality | ⚠️ partial |

### 4.3 Code-quality issues identified in the original `main.py`

1. **SQL-injection risk** — `table`, `limit` and `offset` were interpolated directly into SQL strings via f-strings.
2. **Connection leak on error** — `conn.close()` ran only on the success path (no `try/finally`).
3. **No input validation** — `page=0` or negative/absurd `limit` values were accepted.
4. **No single-record endpoints** for products, customers, orders or categories.
5. **Hardcoded API key** in source (should move to config for production).
6. **`olist.db` did not exist** — the pipeline had never been run in this environment.

---

## 5. Phase 2 — Build the FastAPI Application

### 5.1 Work performed

Rewrote `api/main.py` (v2.1 → v2.2) adding **every required endpoint** while keeping all original routes for backward compatibility:

| Resource | Endpoint | Paginated |
|---|---|---|
| Products | `GET /products` | ✅ |
| Products | `GET /products/{product_id}` | — |
| Customers | `GET /customers` | ✅ |
| Customers | `GET /customers/{customer_id}` | — |
| Orders | `GET /orders` | ✅ |
| Orders | `GET /orders/{order_id}` | — |
| Orders | `GET /orders/{order_id}/details` | — |
| Categories | `GET /categories` | ✅ |
| Categories | `GET /categories/translation` | ✅ |
| (kept) | `/order_items`, `/payments`, `/sellers`, `/reviews`, `/geolocation`, `/category_translation` | ✅ |

### 5.2 Standard pagination envelope (all list endpoints)

```json
{
  "page": 1,
  "limit": 100,
  "total_records": 99441,
  "returned_records": 100,
  "has_next": true,
  "data": [ ... ]
}
```

### 5.3 Hardening added (already Part-6 aligned)

- **Allow-list** (`CATALOG_TABLES`) gates every dynamic table lookup → SQL-injection safe.
- **Parameterized SQL** for `LIMIT`/`OFFSET` and all ID lookups.
- **Input validation** via `Query(ge=1, le=1000)` → invalid pages return `422`.
- **Correct status codes**: `401` bad key, `404` missing record (ID echoed), `500` only for genuine failures.
- **Category aggregation pushed into SQLite** (`GROUP BY` + `COUNT(*)`); products table is never loaded into pandas. Unnamed categories coalesce to `(unknown)`.

### 5.4 First validation round (recorded in §7)

- Generated `olist.db` for the first time: `python scripts/load_data.py`.
- **37/37 smoke tests passed** + a live uvicorn boot (`total_orders=99441`).
  (Final results, including Phase 4, are in [§8](#8-verification--test-results).)

---

## 6. Phase 3 — Code Quality Refactor

### 6.1 Motivation

`api/main.py` had grown to 400 lines. The goal was **modular code** and **reusable functions**, so the single file was split into a proper FastAPI package (v2.2 → v2.3). **API behavior was frozen**: all 16 routes, status codes, auth contract and the pagination envelope are identical.

### 6.2 Final module layout and responsibilities

| Module | Responsibility |
|---|---|
| `api/main.py` | Thin entry point — creates the `FastAPI` app and includes the routers |
| `api/config.py` | Single source of truth: `DB_PATH`, `API_KEY`, `CATALOG_TABLES` allow-list, `TABLE_ID_COLUMNS`, pagination defaults |
| `api/database.py` | `db_connection()` context manager (leak-proof), `dataframe_to_records()`, `paginated_response()`, `validate_pagination()` |
| `api/security.py` | `verify_api_key` FastAPI dependency (`APIKeyHeader`) |
| `api/crud.py` | **All SQL** — `get_paged()`, `get_table()`, `get_record()`, `get_order_details()`, `get_categories()` |
| `api/routers/*.py` | One router per resource; endpoints only map URLs → CRUD calls |

### 6.3 Key design decisions (with rationale)

1. **Auth as a dependency** — each router declares `dependencies=[Depends(verify_api_key)]`. Benefit: FastAPI auto-documents the `x-api-key` scheme, so `/docs` gains a working **Authorize** button; behavior unchanged (missing/wrong key → `401 Invalid API Key`).
2. **`db_connection()` context manager** — connections are guaranteed closed on both success and error paths, structurally eliminating the original leak.
3. **`get_paged(sql, count_sql, params, page, limit)`** — one function drives *every* list endpoint (tables + categories), removing duplicated LIMIT/OFFSET/count/envelope logic.
4. **Aggregation stays in SQL** — the categories total is a `SELECT COUNT(*) FROM (…aggregation…)` subquery; no table is loaded into pandas.
5. **`TABLE_ID_COLUMNS` map** — single-record endpoints reference the primary-key column from config instead of repeating magic strings.

### 6.4 How each code-quality requirement is satisfied

| Requirement | Implementation |
|---|---|
| **Error handling** | `try/except` in every CRUD function with `except HTTPException: raise` (never masks HTTP errors); DB failure → `500` with setup hint; missing rows → `404` echoing the ID |
| **Input validation** | `Query(ge=1, le=1000)` + `Path(min_length=1)` at the border; defensive `validate_pagination()` → `422` |
| **Meaningful variable names** | `get_paged`, `paginated_response`, `db_connection`, `api_key_header`, `max_limit`, … |
| **Comments** | Module docstrings + rationale comments (e.g. why an allow-list prevents SQL injection, why `auto_error=False`) |
| **Modular code** | Routers split per resource; cross-cutting concerns isolated in `config` / `database` / `security` / `crud` |
| **Reusable functions** | `get_paged()` powers all lists; `get_record()` powers all single-record lookups; `verify_api_key` shared by every router; one envelope function for all pagination |

---

## 7. Phase 4 — SQL Layer

The goal: *optimised SQL*, *no full-table loads into pandas*, and *aggregation in SQL*. Three concrete issues were found and fixed.

### 7.1 Issues found and fixed

| # | Issue | Fix |
|---|---|---|
| 1 | Tables were created with **no primary keys, foreign keys or indexes** → every API lookup full-scanned 100K–1M row tables | Rewrote `scripts/load_data.py` with explicit typed DDL, PKs, **enforced** FKs and 13 indexes |
| 2 | **Data corruption** — zip-code prefixes lost leading zeros (`01003` → `1003`), breaking joins to geolocation | `dtype=str` on all zip-prefix columns when reading CSVs |
| 3 | pandas `to_sql` bulk-load was pathologically slow with FK enforcement on | Replaced with parameterized, chunked `executemany` (1M rows in ~2 s; full build in well under a minute) |
| 4 | **No optimised SQL artifacts** existed (Part 4 deliverable missing) | Added `sql/` folder with 15 analytics queries (README + indexed, SQL-only aggregation) |

### 7.2 Schema design decisions

- **Primary keys** on 8 tables; `geolocation` has *no* natural key (1,000,163 rows, 981K duplicate zip prefixes) so it gets an index instead.
- **`reviews` composite PK** `(review_id, order_id)` — the raw `review_id` has 814 duplicates.
- **Foreign keys enforced** (`PRAGMA foreign_keys = ON`) — every relationship verified with zero orphans.
  - Deliberate exception: `products.product_category_name → category_translation` is **not** an FK because 2 categories (623 products) are missing from the translation table.
- **13 indexes** cover every API lookup and analytics join column (`EXPLAIN QUERY PLAN` now shows `SEARCH … USING INDEX` for all of them).
- Source column spelling (`product_name_lenght`) preserved for compatibility.

### 7.3 The `sql/` analytics folder (15 queries)

Aggregation is 100% in SQL — the largest result set is 74 rows. Sample verified results:

| Query | Result |
|---|---|
| 06 Average order value | **€160.56** across 98,815 non-canceled orders |
| 08 Late deliveries | **8.11 %** late (7,826 of 96,470), avg. 11.2 days *early* |
| 10 Payment mix | **credit_card 73.9 %** of payments |
| 01 Top seller | `cama_mesa_banho` product category, 3,029 products — top by units: `moveis_decoracao`, 527 units |

### 7.4 Database rebuild

```bash
python scripts/load_data.py      # drops + recreates olist.db (PK/FK/indexes)
```

All verification for Phase 4 is in [§8](#8-verification--test-results).

---

## 8. Verification & Test Results

### 8.1 Automated smoke tests (FastAPI `TestClient`)

A temporary smoke-test script exercised every endpoint. **Round 1** (after Phase 2): **37/37 passed**. **Round 2** (after Phase 3 refactor): **38/38 passed**. **Round 3** (after Phase 4 schema rebuild): **38/38 still passed** — no API regressions.

Coverage:

| Check group | Status |
|---|---|
| `GET /` home + version | ✅ |
| Auth — missing key → `401`, wrong key → `401` | ✅ |
| List endpoints — `200`, envelope fields, `limit` respected, `has_next` | ✅ |
| Single-record endpoints — `200` matching ID, nonexistent ID → `404` | ✅ |
| `GET /orders/{id}/details` — nested `order`/`items`/`payments`/`reviews` keys | ✅ |
| `GET /categories` — SQL aggregation + envelope | ✅ |
| `GET /categories/translation` — English names present | ✅ |
| Pagination validation — `page=0`, `limit=0`, `limit=5000` → `422` | ✅ |
| Page 2 disjoint from page 1 | ✅ |
| Backward-compat endpoints (`/order_items`, `/payments`, `/sellers`, `/reviews`, `/geolocation`, `/category_translation`) | ✅ |
| OpenAPI security scheme (`x-api-key`) documented | ✅ |

### 8.2 Live server boots (uvicorn)

| Check | Result |
|---|---|
| `GET /orders?limit=1` on port 8013 | `200` — `total_orders=99441` |
| `GET /customers/somebody` (missing) on port 8014 | `404` with error detail |

### 8.3 Static checks

- `python -m compileall api` — clean
- `python -m py_compile` — clean
- No `__pycache__` artifacts left in the repo (cleaned before handover)

### 8.4 Phase 4 SQL verification (new schema)

| Check | Result |
|---|---|
| Table rebuild (`scripts/load_data.py`) | ✅ 9 tables, 1,550,772 rows total, build < 1 min |
| Primary keys declared | ✅ 8 tables (geolocation intentionally none) |
| Foreign-key integrity (`PRAGMA foreign_key_check`) | ✅ **0 violations** |
| Zip-prefix leading zeros | ✅ `01003` preserved; geolocation join hits (26 rows for `01001`) |
| `EXPLAIN QUERY PLAN` on API lookups | ✅ all `SEARCH … USING INDEX` (no table scans) |
| All 15 `sql/` analytics queries | ✅ execute, correct shapes, sample results in §7.3 |

---

## 9. How to Run the Project

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build the database from the CSVs (only needed once)
python scripts/load_data.py

# 3. Start the API
uvicorn api.main:app --reload
```

- Interactive docs: **http://127.0.0.1:8000/docs**
- All endpoints except `/` require the header: `x-api-key: olist-api-2026`
  (the `/docs` UI has an **Authorize** button)
- Example with curl:

```bash
curl -H "x-api-key: olist-api-2026" "http://127.0.0.1:8000/products?page=1&limit=5"
```

---

## 10. Assumptions & Known Limitations

### Assumptions

1. **ID columns are text primary keys** — `order_id`, `customer_id`, `product_id` are 32-char hex strings; the schema now declares them as `TEXT PRIMARY KEY`.
2. **Category semantics** — a product with a null/empty category is reported as `(unknown)` in `/categories` and analytics, not dropped.
3. **Backward compatibility** — pre-existing endpoints are preserved in addition to the required ones.
4. **API key location** — kept in `api/config.py` for demonstration convenience; production should move it to an environment variable.

### Known limitations

| # | Limitation | Status |
|---|---|---|
| 1 | `products.product_category_name → category_translation` has **no FK** (2 categories / 623 products missing from translation); foreign-key enforcement is ON for all other relationships | documented exception |
| 2 | **Analytics endpoints are not yet exposed over HTTP** — the 15 SQL queries exist and are verified, endpoints are the remaining work | planned |
| 3 | API key is hardcoded in `api/config.py` | accepted for this deployment |
| 4 | No permanent test suite in the repo (smoke tests were run from a temp file) | recommend promoting to `tests/` |
| 5 | The Power BI `.pbix` exists but was **not** regenerated as part of this work | dashboard scope untouched |
| 6 | `README.md` still documents the original v2.1 app (endpoint list is a subset) | docs refresh pending |

---

## 11. Next Steps

| Area | Work required |
|---|---|
| **Database** | ✅ Delivered through `scripts/load_data.py` (PKs, enforced FKs, typed columns, indexes) |
| **Advanced Analytics** | Turn the 15 `sql/` queries into FastAPI endpoints (`/analytics/…`) reusing the existing `crud` patterns |
| **SQL** | ✅ Delivered — `sql/` folder (15 queries), indexed schema, `EXPLAIN`-verified |
| **Dashboard** | Refresh/extend the Power BI `.pbix`, connect it to `olist.db`, add required KPIs, trend, map, filters |
| **Documentation** | Refresh `README.md` (endpoint table, run steps, screenshots) and add dashboard screenshots |
| **Quality** | Promote the smoke test to a permanent `tests/test_api.py`; move `API_KEY` to an environment variable |

---

*End of development-process documentation (captures all work up to this point).*