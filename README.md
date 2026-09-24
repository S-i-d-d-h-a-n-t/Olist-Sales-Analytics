# Olist E-commerce API

## Overview

This project contains a REST API built using FastAPI and the Olist E-commerce dataset. It exposes the dataset through a paginated, authenticated REST API backed by a relational SQLite database, and ships with a set of optimised SQL analytics queries and a Power BI dashboard.

---

## Dataset

The CSV datasets are available inside the `data/` folder.

---

## Installation

Clone the repository

```bash
git clone https://github.com/sambhatnagar4/olist-api.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Load Database

Run

```bash
python scripts/load_data.py
```

This will create the SQLite database (`olist.db`).

---

## Start the API

```bash
uvicorn api.main:app --reload
```

---

## API Documentation

After starting the server, open:

```
http://127.0.0.1:8000/docs
```

---

## Authentication

All endpoints require the following API key:

```
olist-api-2026
```

Pass it in the request header:

```
x-api-key: olist-api-2026
```

---

## Available Endpoints

- GET /
- GET /products
- GET /products/{product_id}
- GET /customers
- GET /customers/{customer_id}
- GET /orders
- GET /orders/{order_id}
- GET /orders/{order_id}/details
- GET /categories
- GET /categories/translation
- GET /order_items
- GET /payments
- GET /sellers
- GET /reviews
- GET /geolocation
- GET /category_translation

All endpoints (except `GET /`) require the `x-api-key` header described above.

---

## Documentation

The complete project documentation — installation, dependencies, endpoint reference,
data model, SQL analytics, dashboard and limitations — lives in:

**PROJECT_DOCUMENTATION.md**

The build history is recorded in **DEVELOPMENT_PROCESS.md**.

## Technologies Used

- Python
- FastAPI
- SQLite
- Pandas