"""Load the Olist CSV datasets into a relational SQLite database.

Creates ``olist.db`` with a proper, optimised schema:

* **Primary keys** on every table that has a natural key
  (``geolocation`` has none - 1M rows share zip codes - so it gets an index).
* **Foreign keys** between tables, with ``PRAGMA foreign_keys = ON`` enforced
  (verified: the dataset has zero orphan rows).
* **Indexes** on every join / lookup column used by the API and the
  analytics queries in ``sql/``.

One deliberate exception: ``products.product_category_name`` does **not** get
a foreign key to ``category_translation`` because 2 categories (623 products)
exist in products but not in the translation table.

Run:  python scripts/load_data.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "olist.db"

# CSV column order MUST match the CREATE TABLE column order below.
FILES = {
    "category_translation": "product_category_name_translation.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
}

# Tables are listed in dependency order so foreign-key inserts always have
# their referenced row already present. Column order matches each CSV.
DDL = {
    "category_translation": """
        CREATE TABLE category_translation (
            product_category_name         TEXT PRIMARY KEY,
            product_category_name_english TEXT NOT NULL
        )""",
    "customers": """
        CREATE TABLE customers (
            customer_id                TEXT PRIMARY KEY,
            customer_unique_id         TEXT NOT NULL,
            customer_zip_code_prefix   TEXT,
            customer_city              TEXT,
            customer_state             TEXT
        )""",
    "products": """
        CREATE TABLE products (
            product_id                  TEXT PRIMARY KEY,
            product_category_name       TEXT,
            -- NOTE: 'lenght' spelling is from the source CSV and kept on purpose
            product_name_lenght         INTEGER,
            product_description_lenght  INTEGER,
            product_photos_qty          INTEGER,
            product_weight_g            REAL,
            product_length_cm           REAL,
            product_height_cm           REAL,
            product_width_cm            REAL
        )""",
    "sellers": """
        CREATE TABLE sellers (
            seller_id              TEXT PRIMARY KEY,
            seller_zip_code_prefix TEXT,
            seller_city            TEXT,
            seller_state           TEXT
        )""",
    "orders": """
        CREATE TABLE orders (
            order_id                       TEXT PRIMARY KEY,
            customer_id                    TEXT NOT NULL REFERENCES customers(customer_id),
            order_status                   TEXT,
            order_purchase_timestamp       TEXT,
            order_approved_at              TEXT,
            order_delivered_carrier_date   TEXT,
            order_delivered_customer_date  TEXT,
            order_estimated_delivery_date  TEXT
        )""",
    "order_items": """
        CREATE TABLE order_items (
            order_id            TEXT NOT NULL REFERENCES orders(order_id),
            order_item_id       INTEGER NOT NULL,
            product_id          TEXT NOT NULL REFERENCES products(product_id),
            seller_id           TEXT NOT NULL REFERENCES sellers(seller_id),
            shipping_limit_date TEXT,
            price               REAL,
            freight_value       REAL,
            PRIMARY KEY (order_id, order_item_id)
        )""",
    "payments": """
        CREATE TABLE payments (
            order_id            TEXT NOT NULL REFERENCES orders(order_id),
            payment_sequential  INTEGER NOT NULL,
            payment_type        TEXT,
            payment_installments INTEGER,
            payment_value       REAL,
            PRIMARY KEY (order_id, payment_sequential)
        )""",
    "reviews": """
        CREATE TABLE reviews (
            review_id              TEXT NOT NULL,
            order_id               TEXT NOT NULL REFERENCES orders(order_id),
            review_score           INTEGER,
            review_comment_title   TEXT,
            review_comment_message TEXT,
            review_creation_date    TEXT,
            review_answer_timestamp TEXT,
            -- review_id alone is NOT unique, hence the composite key
            PRIMARY KEY (review_id, order_id)
        )""",
    "geolocation": """
        CREATE TABLE geolocation (
            geolocation_zip_code_prefix TEXT,
            geolocation_lat             REAL,
            geolocation_lng             REAL,
            geolocation_city            TEXT,
            geolocation_state           TEXT
        )""",
}

# Indexes for the columns the API and analytics queries filter / join on.
INDEXES = [
    "CREATE INDEX idx_customers_unique_id ON customers(customer_unique_id)",
    "CREATE INDEX idx_customers_state     ON customers(customer_state)",
    "CREATE INDEX idx_customers_zip       ON customers(customer_zip_code_prefix)",
    "CREATE INDEX idx_products_category   ON products(product_category_name)",
    "CREATE INDEX idx_sellers_zip         ON sellers(seller_zip_code_prefix)",
    "CREATE INDEX idx_orders_customer     ON orders(customer_id)",
    "CREATE INDEX idx_orders_purchase_ts  ON orders(order_purchase_timestamp)",
    "CREATE INDEX idx_items_product       ON order_items(product_id)",
    "CREATE INDEX idx_items_seller        ON order_items(seller_id)",
    "CREATE INDEX idx_payments_type       ON payments(payment_type)",
    "CREATE INDEX idx_reviews_order       ON reviews(order_id)",
    "CREATE INDEX idx_geolocation_zip     ON geolocation(geolocation_zip_code_prefix)",
    "CREATE INDEX idx_geolocation_state   ON geolocation(geolocation_state)",
]

# Column names that must stay text even though they look numeric, so leading
# zeros survive ("01003" must NOT become the integer 1003 - it would break
# joins against the geolocation table).
ZIP_PREFIX_COLUMNS = {
    "customer_zip_code_prefix": str,
    "seller_zip_code_prefix": str,
    "geolocation_zip_code_prefix": str,
}

# Rows per executemany batch (keeps memory flat on the 1M-row geolocation).
_INSERT_BATCH = 50_000


def _bulk_insert(conn: sqlite3.Connection, table: str, df: pd.DataFrame) -> int:
    """Insert a DataFrame using parameterized executemany (fast, FK-safe).

    Much faster than pandas ``to_sql`` for large frames. pandas NaN is
    normalized to SQL NULL so the database stores clean missing values.
    """
    columns = ", ".join(f'"{col}"' for col in df.columns)
    placeholders = ", ".join("?" * len(df.columns))
    insert_sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    clean = df.where(pd.notnull(df), None)          # NaN -> NULL
    records = clean.itertuples(index=False, name=None)

    total = 0
    batch: list[tuple] = []
    for record in records:
        batch.append(record)
        if len(batch) >= _INSERT_BATCH:
            conn.executemany(insert_sql, batch)
            total += len(batch)
            batch.clear()
    if batch:
        conn.executemany(insert_sql, batch)
        total += len(batch)

    return total


def main() -> None:
    conn = sqlite3.connect(DB_PATH)

    # Speed up bulk loading (safe: a crash just leaves a rebuildable DB).
    conn.execute("PRAGMA synchronous = OFF")
    conn.execute("PRAGMA foreign_keys = ON")

    # Rebuild schema from scratch.
    for table in DDL:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.execute(DDL[table])

    # Load data in FK dependency order.
    for table, filename in FILES.items():
        csv_path = DATA_DIR / filename
        print(f"Loading {filename} ...", end=" ", flush=True)
        df = pd.read_csv(csv_path, dtype=ZIP_PREFIX_COLUMNS)
        rows = _bulk_insert(conn, table, df)
        print(f"{rows:,} rows")

    # Add the analytical indexes last (fastest build order).
    for create_index_sql in INDEXES:
        conn.execute(create_index_sql)

    conn.execute("PRAGMA optimize")  # refresh query-planner statistics
    conn.commit()
    conn.close()

    print("\n✅ Database created successfully!")
    print(f"Database saved at: {DB_PATH}")


if __name__ == "__main__":
    main()