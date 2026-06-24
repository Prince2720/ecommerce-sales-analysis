"""
fast_load.py
Loads all Olist CSV files into MySQL in one go.
Automatically reads column names from CSV — no schema mismatch errors.

SETUP:
    pip install pandas sqlalchemy pymysql

USAGE:
    1. Fill in your MySQL password below
    2. Update DATA_PATH to your brazilian_ecommerce folder path
    3. Run: python fast_load.py
"""

import pandas as pd
from sqlalchemy import create_engine, text
import time

# ---------------------------------------------------------------
# CONFIGURATION — update these two lines only
# ---------------------------------------------------------------
MYSQL_PASSWORD = "Prince2720"       # your MySQL root password
DATA_PATH      = r"D:\brazilian_ecommerce"  # path to your CSV folder
# ---------------------------------------------------------------

DB_NAME = "olist_ecommerce"

engine = create_engine(
    f"mysql+pymysql://root:{MYSQL_PASSWORD}@localhost/{DB_NAME}",
    echo=False
)

# Files to load in correct order (parents before children)
FILES = [
    ("olist_customers_dataset.csv",      "customers"),
    ("olist_products_dataset.csv",       "products"),
    ("olist_sellers_dataset.csv",        "sellers"),
    ("olist_orders_dataset.csv",         "orders"),
    ("olist_order_items_dataset.csv",    "order_items"),
    ("olist_order_payments_dataset.csv", "order_payments"),
    ("olist_order_reviews_dataset.csv",  "order_reviews"),
]

print("=" * 55)
print("  Olist E-Commerce -- Fast MySQL Loader")
print("=" * 55)

total_start = time.time()

with engine.connect() as conn:

    # Disable FK checks so truncate works freely
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    conn.commit()
    print("\nForeign key checks disabled.")

    for csv_file, table_name in FILES:
        file_path = f"{DATA_PATH}\\{csv_file}"
        print(f"\nLoading {csv_file} -> table: {table_name}")
        start = time.time()

        try:
            # Read CSV first to get actual column names
            df = pd.read_csv(file_path, low_memory=False)

            # Drop and recreate table using CSV column names (no mismatch)
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists="replace",   # drops & recreates with correct columns
                index=False,
                chunksize=1000
            )
            elapsed = round(time.time() - start, 1)
            print(f"  OK -- {len(df):,} rows loaded in {elapsed}s")

        except FileNotFoundError:
            print(f"  ERROR: File not found: {file_path}")
            print(f"         Check your DATA_PATH setting above.")

        except Exception as e:
            print(f"  ERROR loading {table_name}: {e}")

    # Re-enable FK checks
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    conn.commit()
    print("\nForeign key checks re-enabled.")

total_elapsed = round(time.time() - total_start, 1)
print(f"\n{'='*55}")
print(f"  All files processed in {total_elapsed}s")
print(f"  Verify in MySQL Workbench:")
print(f"  USE olist_ecommerce;")
print(f"  SELECT COUNT(*) FROM customers;   -- should be 99,441")
print(f"  SELECT COUNT(*) FROM orders;      -- should be 99,441")
print(f"  SELECT COUNT(*) FROM order_items; -- should be 112,650")
print(f"{'='*55}")