"""Reusable data-access layer: every SQL statement lives here.

Routers stay thin and declarative - they only map URL patterns on to these
functions. Aggregation is pushed down to SQLite instead of pandas so whole
tables are never loaded into memory.
"""
import pandas as pd
from fastapi import HTTPException

from .config import CATALOG_TABLES
from .database import (
    dataframe_to_records,
    db_connection,
    paginated_response,
    validate_pagination,
)


def get_paged(sql: str, count_sql: str, params: tuple, page: int, limit: int) -> dict:
    """Run ``sql`` (with LIMIT/OFFSET appended) and paginate its results."""
    offset = validate_pagination(page, limit)
    try:
        with db_connection() as conn:
            total = int(pd.read_sql(count_sql, conn).iloc[0]["total"])
            df = pd.read_sql(
                f"{sql} LIMIT ? OFFSET ?",
                conn,
                params=(*params, limit, offset),
            )
    except HTTPException:
        raise  # already an HTTP-level error - do not mask it
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")
    return paginated_response(df, page, limit, total)


def get_table(table: str, page: int, limit: int) -> dict:
    """Return one page of rows from a whitelisted table."""
    if table not in CATALOG_TABLES:
        raise HTTPException(status_code=404, detail=f"Unknown table '{table}'")
    return get_paged(
        sql=f"SELECT * FROM {table}",
        count_sql=f"SELECT COUNT(*) AS total FROM {table}",
        params=(),
        page=page,
        limit=limit,
    )


def get_record(table: str, id_column: str, id_value) -> dict:
    """Return a single row by primary key, or raise 404 when missing."""
    try:
        with db_connection() as conn:
            df = pd.read_sql(
                f"SELECT * FROM {table} WHERE {id_column} = ?",
                conn,
                params=(str(id_value),),
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read '{table}': {e}")

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Record not found in '{table}' with {id_column} = '{id_value}'",
        )
    return dataframe_to_records(df)[0]


def get_order_details(order_id: str) -> dict:
    """Load one order plus its items, payments and reviews (404 when missing)."""
    try:
        with db_connection() as conn:
            order = pd.read_sql(
                "SELECT * FROM orders WHERE order_id = ?",
                conn,
                params=(order_id,),
            )
            if order.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"Order not found: '{order_id}'",
                )
            items = pd.read_sql(
                "SELECT * FROM order_items WHERE order_id = ?",
                conn,
                params=(order_id,),
            )
            payments = pd.read_sql(
                "SELECT * FROM payments WHERE order_id = ?",
                conn,
                params=(order_id,),
            )
            reviews = pd.read_sql(
                "SELECT * FROM reviews WHERE order_id = ?",
                conn,
                params=(order_id,),
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load order details: {e}")

    return {
        "order": dataframe_to_records(order)[0],
        "items": dataframe_to_records(items),
        "payments": dataframe_to_records(payments),
        "reviews": dataframe_to_records(reviews),
    }


# Distinct product categories aggregated in SQLite; unnamed rows -> '(unknown)'.
CATEGORY_AGG_SQL = """
SELECT
    CASE
        WHEN product_category_name IS NULL OR product_category_name = ''
        THEN '(unknown)'
        ELSE product_category_name
    END AS category,
    COUNT(*) AS product_count
FROM products
GROUP BY 1
ORDER BY product_count DESC
"""


def get_categories(page: int, limit: int) -> dict:
    """Return product categories ranked by product count (paginated)."""
    return get_paged(
        sql=CATEGORY_AGG_SQL,
        count_sql=f"SELECT COUNT(*) AS total FROM ({CATEGORY_AGG_SQL})",
        params=(),
        page=page,
        limit=limit,
    )