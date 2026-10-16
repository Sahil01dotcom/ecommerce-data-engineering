import pandas as pd
from pathlib import Path


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Sample data directory
DATA_DIR = PROJECT_ROOT / "data" / "sample"


def inspect_file(filename):
    """Read and inspect a CSV file."""

    file_path = DATA_DIR / filename

    print("\n" + "=" * 60)
    print(f"FILE: {filename}")
    print("=" * 60)

    df = pd.read_csv(file_path)

    print(f"\nRows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Rows:")
    print(df.duplicated().sum())

    print("\nFirst 5 Rows:")
    print(df.head())


def main():

    files = [
        "customers.csv",
        "products.csv",
        "orders.csv",
        "order_items.csv",
        "payments.csv"
    ]

    for file in files:
        inspect_file(file)


if __name__ == "__main__":
    main()