"""Customer endpoints."""
from fastapi import APIRouter, Depends, Path, Query

from ..config import DEFAULT_LIMIT, DEFAULT_PAGE, MAX_LIMIT
from ..crud import get_record, get_table
from ..security import verify_api_key

router = APIRouter(prefix="/customers", tags=["customers"], dependencies=[Depends(verify_api_key)])


@router.get("")
def list_customers(
    page: int = Query(DEFAULT_PAGE, ge=1),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    """List customers (paginated)."""
    return get_table("customers", page, limit)


@router.get("/{customer_id}")
def get_customer(customer_id: str = Path(..., min_length=1)):
    """Return a single customer by id."""
    return get_record("customers", "customer_id", customer_id)