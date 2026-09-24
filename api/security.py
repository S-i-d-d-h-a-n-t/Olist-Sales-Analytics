"""API-key authentication shared by every protected router."""
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from .config import API_KEY

# Reads the ``x-api-key`` header. auto_error=False lets this code return its
# own consistent 401 (instead of FastAPI's default 403), matching the API
# contract every client already expects.
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def verify_api_key(x_api_key: str = Depends(api_key_header)) -> None:
    """FastAPI dependency: reject requests that lack the valid API key."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")