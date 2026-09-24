"""Product endpoints."""
from fastapi import APIRouter, Depends, Path, Query

from ..config import DEFAULT_LIMIT, DEFAULT_PAGE, MAX_LIMIT
from ..crud import get_record, get_table
from ..security import verify_api_key

router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(verify_api_key)])


@router.get("")
def list_products(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List products (paginated)."""
    return get_table("products", page, limit)


@router.get("/{product_id}")
def get_product(product_id: str = Path(..., min_length=1)):
    """Return a single product by id."""
    return get_record("products", "product_id", product_id)