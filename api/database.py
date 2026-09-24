"""Database connection management and JSON-safe data shaping."""
import sqlite3
from contextlib import contextmanager

import pandas as pd
from fastapi import HTTPException

from .config import DB_PATH, MAX_LIMIT

_SETUP_HINT = "Run 'python scripts/load_data.py' before starting the API."


@contextmanager
def db_connection() -> sqlite3.Connection:
    """Yield an open SQLite connection that is always closed afterwards.

    Designed to be used with ``with`` so callers can never leak connections,
    even when an exception is raised mid-query.
    """
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Database not found at {DB_PATH}. {_SETUP_HINT}",
        )
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert a DataFrame to JSON-safe records (pandas NaN -> null)."""
    return df.where(pd.notnull(df), None).to_dict(orient="records")


def paginated_response(df: pd.DataFrame, page: int, limit: int, total: int) -> dict:
    """Build the standard pagination envelope shared by every list endpoint."""
    return {
        "page": page,
        "limit": limit,
        "total_records": int(total),
        "returned_records": int(len(df)),
        "has_next": bool((page - 1) * limit + len(df) < total),
        "data": dataframe_to_records(df),
    }


def validate_pagination(page: int, limit: int) -> int:
    """Defensive page/limit checks (FastAPI also validates at the border).

    Returns the SQL OFFSET for the given page.
    """
    if page < 1:
        raise HTTPException(status_code=422, detail="page must be >= 1")
    if limit < 1 or limit > MAX_LIMIT:
        raise HTTPException(status_code=422, detail=f"limit must be between 1 and {MAX_LIMIT}")
    return (page - 1) * limit


print(f"Database Path: {DB_PATH}")
print(f"Database Exists: {DB_PATH.exists()}")