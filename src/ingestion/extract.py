
import pandas as pd
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "data" / "sample"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Expected schemas
SCHEMAS = {
    "customers.csv": [
        "customer_id", "first_name", "last_name",
        "email", "city", "state", "signup_date"
    ],
    "products.csv": [
        "product_id", "product_name", "category",
        "price", "stock_quantity"
    ],
    "orders.csv": [
        "order_id", "customer_id", "order_date",
        "order_status", "payment_method"
    ],
    "order_items.csv": [
        "order_item_id", "order_id", "product_id",
        "quantity", "unit_price", "discount"
    ],
    "payments.csv": [
        "payment_id", "order_id",
        "payment_amount", "payment_status"
    ]
}

def validate_data(df, filename):
    """Validate the basic structure of a dataset."""

    expected_columns = SCHEMAS[filename]

    if list(df.columns) != expected_columns:
        raise ValueError(
            f"Invalid schema in {filename}"
        )

    if df.empty:
        raise ValueError(
            f"Empty dataset: {filename}"
        )

    print(f"Validated: {filename}")
    print(f"Records: {len(df)}")

def run_pipeline():
    """Ingest validated source files into the raw layer."""

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%S%fZ")

    batch_dir = RAW_DIR / timestamp
    batch_dir.mkdir(parents=True, exist_ok=False)

    print("Starting ingestion pipeline")

    for filename in SCHEMAS:
        source = SOURCE_DIR / filename

        if not source.exists():
            raise FileNotFoundError(source)

        df = pd.read_csv(source)

        validate_data(df, filename)

        destination = batch_dir / filename

        # Preserve the original CSV without modification.
        shutil.copy2(source, destination)

        print(f"Saved: {destination}\n")

    print("Ingestion completed successfully!")

if __name__ == "__main__":
    run_pipeline()
