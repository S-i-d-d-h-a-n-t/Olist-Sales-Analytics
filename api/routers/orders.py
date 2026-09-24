"""Order endpoints."""
from fastapi import APIRouter, Depends, Path, Query

from ..config import DEFAULT_LIMIT, DEFAULT_PAGE, MAX_LIMIT
from ..crud import get_order_details, get_record, get_table
from ..security import verify_api_key

router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verify_api_key)])


@router.get("")
def list_orders(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List orders (paginated)."""
    return get_table("orders", page, limit)


@router.get("/{order_id}")
def get_order(order_id: str = Path(..., min_length=1)):
    """Return a single order by id."""
    return get_record("orders", "order_id", order_id)


@router.get("/{order_id}/details")
def order_details(order_id: str = Path(..., min_length=1)):
    """Nested view of one order: its items, payments and reviews."""
    return get_order_details(order_id)