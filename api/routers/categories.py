"""Category endpoints."""
from fastapi import APIRouter, Depends, Query

from ..config import DEFAULT_LIMIT, DEFAULT_PAGE, MAX_LIMIT
from ..crud import get_categories, get_table
from ..security import verify_api_key

router = APIRouter(prefix="/categories", tags=["categories"], dependencies=[Depends(verify_api_key)])


@router.get("")
def list_categories(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List distinct product categories ranked by product count."""
    return get_categories(page, limit)


@router.get("/translation")
def categories_translation(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List the product-category to English translation table (paginated)."""
    return get_table("category_translation", page, limit)