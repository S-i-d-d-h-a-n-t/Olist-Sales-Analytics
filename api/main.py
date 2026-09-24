"""Olist E-commerce API - application entry point.

Run with:
    uvicorn api.main:app --reload
"""
from fastapi import FastAPI

from .routers import catalog, categories, customers, orders, products

app = FastAPI(
    title="Olist E-commerce API",
    description="REST API for the Olist E-commerce dataset.",
    version="2.3",
)

# Combine the resource routers into one application. Each router handles its
# own authentication via the shared ``verify_api_key`` dependency.
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(categories.router)
app.include_router(catalog.router)


@app.get("/", tags=["meta"])
def home():
    """Simple home endpoint (no authentication)."""
    return {
        "message": "Welcome to Olist E-commerce API",
        "version": app.version,
    }