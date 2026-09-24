"""Centralised configuration for the Olist E-commerce API.

Every setting lives here so routers, CRUD helpers and tests all read from
one place instead of repeating magic values across modules.
"""
from pathlib import Path

# --------------------------------------------------------------------------
# Project layout
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "olist.db"

# --------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------
API_KEY = "olist-api-2026"

# --------------------------------------------------------------------------
# Tables exposed through the generic list endpoints.
#
# The allow-list keeps dynamic table lookups SQL-injection safe: a request
# value can never reference a table outside of this set.
# --------------------------------------------------------------------------
CATALOG_TABLES = frozenset({
    "customers",
    "orders",
    "order_items",
    "payments",
    "products",
    "sellers",
    "reviews",
    "geolocation",
    "category_translation",
})

# Primary-key columns used by the single-record endpoints.
TABLE_ID_COLUMNS = {
    "customers": "customer_id",
    "orders": "order_id",
    "products": "product_id",
}

# --------------------------------------------------------------------------
# Pagination defaults
# --------------------------------------------------------------------------
DEFAULT_PAGE = 1
DEFAULT_LIMIT = 100
MAX_LIMIT = 1000