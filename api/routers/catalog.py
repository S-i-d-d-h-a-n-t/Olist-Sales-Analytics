"""Backwards-compatible endpoints for the remaining catalog tables."""
from fastapi import APIRouter, Depends, Query

from ..config import DEFAULT_LIMIT, DEFAULT_PAGE, MAX_LIMIT
from ..crud import get_table
from ..security import verify_api_key

router = APIRouter(tags=["catalog"], dependencies=[Depends(verify_api_key)])


@router.get("/order_items")
def list_order_items(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List order_items (paginated)."""
    return get_table("order_items", page, limit)


@router.get("/payments")
def list_payments(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List payments (paginated)."""
    return get_table("payments", page, limit)


@router.get("/sellers")
def list_sellers(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List sellers (paginated)."""
    return get_table("sellers", page, limit)


@router.get("/reviews")
def list_reviews(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List reviews (paginated)."""
    return get_table("reviews", page, limit)


@router.get("/geolocation")
def list_geolocation(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List geolocation entries (paginated)."""
    return get_table("geolocation", page, limit)


@router.get("/category_translation")
def list_category_translation(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List the category translation table (paginated)."""
    return get_table("category_translation", page, limit)