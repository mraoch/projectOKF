"""
Load the Aai-Food CSV files into PostgreSQL.

Safe to run again: the tables are dropped and loaded fresh every time.

    python scripts/ingest_data.py
or, from the notebook:
    from scripts.ingest_data import main; main()
"""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
load_dotenv(PROJECT_DIR / ".env")


# =============================================================================
# Table definitions
# =============================================================================

CREATE_RESTAURANTS = """
CREATE TABLE restaurants (
    restaurant_id      TEXT PRIMARY KEY,
    restaurant_name    TEXT         NOT NULL,
    cuisine            TEXT         NOT NULL,
    city               TEXT         NOT NULL,
    area               TEXT         NOT NULL,
    rating             NUMERIC(2,1) NOT NULL,
    avg_prep_time_min  INTEGER      NOT NULL,
    is_active          BOOLEAN      NOT NULL,
    joined_on          DATE         NOT NULL
);
"""

CREATE_ORDERS = """
CREATE TABLE orders (
    order_id            TEXT PRIMARY KEY,
    customer_id         TEXT         NOT NULL,
    restaurant_id       TEXT         NOT NULL REFERENCES restaurants (restaurant_id),
    city                TEXT         NOT NULL,
    order_placed_at     TIMESTAMP    NOT NULL,
    order_delivered_at  TIMESTAMP,                 -- NULL for cancelled orders
    status              TEXT         NOT NULL CHECK (status IN ('Delivered', 'Cancelled')),
    order_value_inr     INTEGER      NOT NULL,
    delivery_fee_inr    INTEGER      NOT NULL,
    discount_inr        INTEGER      NOT NULL,
    payment_method      TEXT         NOT NULL,
    rider_id            TEXT,                      -- NULL for cancelled orders
    distance_km         NUMERIC(3,1) NOT NULL,
    weather             TEXT         NOT NULL CHECK (weather IN ('Clear', 'Rain', 'Heavy Rain')),
    customer_rating     SMALLINT                   -- NULL for cancelled orders
);
"""


# =============================================================================
# Steps
# =============================================================================

def connect(dbname):
    """Connect as the admin user from .env."""
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD"),
        dbname=dbname,
    )


def create_database(db_name):
    """Create the database if it doesn't exist yet."""
    conn = connect("postgres")
    conn.autocommit = True   # CREATE DATABASE can't run inside a transaction
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if cur.fetchone():
            print(f"Database '{db_name}' already exists")
        else:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"Database '{db_name}' created")
    conn.close()


def load_csv(cur, table, csv_path):
    """Bulk-load a CSV file with COPY. Empty cells become NULL."""
    with open(csv_path, encoding="utf-8") as f:
        cur.copy_expert(f"COPY {table} FROM STDIN WITH (FORMAT csv, HEADER true)", f)
    print(f"Loaded {cur.rowcount} rows into {table}")


def create_reader_role(cur, db_name):
    """Create okf_reader: the user the AI agents connect with. It can only SELECT."""
    password = os.getenv("PG_READER_PASSWORD")
    if not password:
        raise ValueError("PG_READER_PASSWORD is missing in .env")

    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = 'okf_reader'")
    if not cur.fetchone():
        cur.execute("CREATE ROLE okf_reader LOGIN")
    cur.execute(sql.SQL("ALTER ROLE okf_reader WITH LOGIN PASSWORD {}").format(sql.Literal(password)))

    cur.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO okf_reader").format(sql.Identifier(db_name)))
    cur.execute("GRANT USAGE ON SCHEMA public TO okf_reader")
    cur.execute("GRANT SELECT ON restaurants, orders TO okf_reader")
    print("Read-only user 'okf_reader' ready")


def print_summary(cur):
    print("\nSummary")
    for table in ("restaurants", "orders"):
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table:<12} {cur.fetchone()[0]:>4} rows")

    print("\n  Orders by status")
    cur.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status")
    for status, count in cur.fetchall():
        print(f"  {status:<12} {count:>4}")


# =============================================================================
# Main
# =============================================================================

def main():
    db_name = os.getenv("PG_DB", "aai_food")
    create_database(db_name)

    conn = connect(db_name)
    with conn, conn.cursor() as cur:   # one transaction: if anything fails, nothing is saved
        # 1. Fresh tables (orders first, because it points to restaurants)
        cur.execute("DROP TABLE IF EXISTS orders")
        cur.execute("DROP TABLE IF EXISTS restaurants")
        cur.execute(CREATE_RESTAURANTS)
        cur.execute(CREATE_ORDERS)
        print("Tables restaurants and orders created")

        # 2. Data (restaurants first, so every order's restaurant_id already exists)
        load_csv(cur, "restaurants", DATA_DIR / "restaurants.csv")
        load_csv(cur, "orders", DATA_DIR / "orders.csv")

        # 3. Read-only user for the AI agents
        create_reader_role(cur, db_name)

        print_summary(cur)
    conn.close()


if __name__ == "__main__":
    main()
