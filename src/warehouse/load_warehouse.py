
import os
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"

load_dotenv(PROJECT_ROOT / ".env")

CENT = Decimal("0.01")


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def read_csv(filename):
    """Read a source CSV file and validate that it exists."""
    path = SAMPLE_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    return pd.read_csv(path)


def decimal_value(value):
    """Convert a value to Decimal without floating-point arithmetic."""
    return Decimal(str(value))


def calculate_sales_amount(quantity, unit_price, discount):
    """Calculate line revenue using standard financial rounding."""
    amount = (
        Decimal(str(int(quantity)))
        * decimal_value(unit_price)
        * (Decimal("1") - decimal_value(discount))
    )

    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def require_columns(df, required_columns, filename):
    """Fail early if a source CSV is missing required columns."""
    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(
            f"{filename} is missing required columns: {sorted(missing)}"
        )


# --------------------------------------------------
# 3. LOAD AND VALIDATE SOURCE DATA
# --------------------------------------------------

def main():
    customers = read_csv("customers.csv")
    products = read_csv("products.csv")
    orders = read_csv("orders.csv")
    items = read_csv("order_items.csv")

    require_columns(
        customers,
        [
            "customer_id", "first_name", "last_name",
            "email", "city", "state", "signup_date"
        ],
        "customers.csv",
    )

    require_columns(
        products,
        [
            "product_id", "product_name", "category",
            "price", "stock_quantity"
        ],
        "products.csv",
    )

    require_columns(
        orders,
        ["order_id", "customer_id", "order_date", "order_status"],
        "orders.csv",
    )

    require_columns(
        items,
        [
            "order_id", "product_id", "quantity",
            "unit_price", "discount"
        ],
        "order_items.csv",
    )

    # Convert dates and numeric fields.
    customers["signup_date"] = pd.to_datetime(
        customers["signup_date"], errors="coerce"
    ).dt.date

    orders["order_date"] = pd.to_datetime(
        orders["order_date"], errors="coerce"
    ).dt.date

    for column in ["quantity", "unit_price", "discount"]:
        items[column] = pd.to_numeric(items[column], errors="coerce")

    # Reject missing or duplicate dimension identifiers.
    if customers["customer_id"].isna().any():
        raise ValueError("customers.csv contains missing customer IDs.")

    if customers["customer_id"].duplicated().any():
        raise ValueError("customers.csv contains duplicate customer IDs.")

    if products["product_id"].isna().any():
        raise ValueError("products.csv contains missing product IDs.")

    if products["product_id"].duplicated().any():
        raise ValueError("products.csv contains duplicate product IDs.")

    if orders["order_id"].isna().any():
        raise ValueError("orders.csv contains missing order IDs.")

    if orders["order_id"].duplicated().any():
        raise ValueError("orders.csv contains duplicate order IDs.")

    if items[
        ["order_id", "product_id", "quantity", "unit_price", "discount"]
    ].isna().any().any():
        raise ValueError("order_items.csv contains missing required values.")

    if not items["quantity"].apply(
        lambda value: float(value).is_integer()
    ).all():
        raise ValueError("Order item quantities must be whole numbers.")

    if (items["quantity"] <= 0).any():
        raise ValueError("Order item quantities must be greater than zero.")

    if (items["unit_price"] < 0).any():
        raise ValueError("Unit prices cannot be negative.")

    if not items["discount"].between(0, 1).all():
        raise ValueError("Discount must be between 0 and 1.")

    if products["price"].isna().any() or (products["price"] < 0).any():
        raise ValueError("Product prices must be present and non-negative.")

    # Exclude cancelled orders and orders without valid dates/customers.
    active_orders = orders[
        orders["order_status"].astype(str).str.lower() != "cancelled"
    ].copy()

    active_orders = active_orders[
        active_orders["order_date"].notna()
        & active_orders["customer_id"].isin(customers["customer_id"])
    ].copy()

    # Keep only order items belonging to active orders and known products.
    valid_items = items[
        items["order_id"].isin(active_orders["order_id"])
        & items["product_id"].isin(products["product_id"])
    ].copy()

    # Fail instead of silently dropping source rows.
    invalid_order_ids = set(items["order_id"]) - set(orders["order_id"])
    invalid_product_ids = set(items["product_id"]) - set(products["product_id"])

    if invalid_order_ids:
        raise ValueError(
            f"Order items reference unknown order IDs: {sorted(invalid_order_ids)[:10]}"
        )

    if invalid_product_ids:
        raise ValueError(
            f"Order items reference unknown product IDs: {sorted(invalid_product_ids)[:10]}"
        )

    if valid_items.empty:
        raise ValueError("No valid order items remain to load.")

    # Prepare source lookups.
    customer_lookup = customers.set_index("customer_id")
    order_lookup = active_orders.set_index("order_id").to_dict("index")

    # Build distinct city/state combinations.
    locations = (
        customers[["city", "state"]]
        .fillna("")
        .drop_duplicates()
        .sort_values(["state", "city"])
        .reset_index(drop=True)
    )

    # Build a distinct date dimension from active order dates.
    date_values = sorted(set(active_orders["order_date"]))

    # --------------------------------------------------
    # 4. CONNECT TO POSTGRESQL
    # --------------------------------------------------

    password = os.getenv("DB_PASSWORD")

    if not password:
        raise ValueError(
            "DB_PASSWORD is missing. Check the project-root .env file."
        )

    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "ecommerce_dw"),
        user=os.getenv("DB_USER", "postgres"),
        password=password,
        connect_timeout=5,
    )

    try:
        # All database changes commit together or roll back together.
        with connection:
            with connection.cursor() as cursor:

                # Full refresh: only use with this project's warehouse.
                cursor.execute(
                    """
                    TRUNCATE TABLE
                        fact_sales,
                        dim_date,
                        dim_location,
                        dim_product,
                        dim_customer
                    RESTART IDENTITY CASCADE
                    """
                )

                # --------------------------------------------------
                # 5. LOAD CUSTOMER DIMENSION
                # --------------------------------------------------

                for _, row in customers.iterrows():
                    full_name = (
                        f"{row['first_name']} {row['last_name']}"
                    ).strip()

                    cursor.execute(
                        """
                        INSERT INTO dim_customer
                            (customer_id, customer_name, email, signup_date)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            int(row["customer_id"]),
                            full_name,
                            row["email"] if pd.notna(row["email"]) else None,
                            row["signup_date"],
                        ),
                    )

                # --------------------------------------------------
                # 6. LOAD PRODUCT DIMENSION
                # --------------------------------------------------

                for _, row in products.iterrows():
                    cursor.execute(
                        """
                        INSERT INTO dim_product
                            (product_id, product_name, category,
                             price, stock_quantity)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            int(row["product_id"]),
                            str(row["product_name"]),
                            row["category"]
                            if pd.notna(row["category"]) else None,
                            decimal_value(row["price"]),
                            int(row["stock_quantity"]),
                        ),
                    )

                # --------------------------------------------------
                # 7. LOAD LOCATION DIMENSION
                # --------------------------------------------------

                for _, row in locations.iterrows():
                    cursor.execute(
                        """
                        INSERT INTO dim_location (city, state, country)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            row["city"] or None,
                            row["state"] or None,
                            "India",
                        ),
                    )

                # Retrieve generated customer keys.
                cursor.execute(
                    "SELECT customer_id, customer_key FROM dim_customer"
                )
                customer_keys = dict(cursor.fetchall())

                # Retrieve generated product keys.
                cursor.execute(
                    "SELECT product_id, product_key FROM dim_product"
                )
                product_keys = dict(cursor.fetchall())

                # Retrieve generated location keys.
                cursor.execute(
                    "SELECT location_key, city, state FROM dim_location"
                )
                location_keys = {
                    (city or "", state or ""): key
                    for key, city, state in cursor.fetchall()
                }

                # --------------------------------------------------
                # 8. LOAD DATE DIMENSION
                # --------------------------------------------------

                for date_value in date_values:
                    date_key = int(date_value.strftime("%Y%m%d"))

                    cursor.execute(
                        """
                        INSERT INTO dim_date
                            (date_key, full_date, day, month,
                             month_name, quarter, year)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            date_key,
                            date_value,
                            date_value.day,
                            date_value.month,
                            date_value.strftime("%B"),
                            (date_value.month - 1) // 3 + 1,
                            date_value.year,
                        ),
                    )

                date_keys = {
                    date_value: int(date_value.strftime("%Y%m%d"))
                    for date_value in date_values
                }

                # --------------------------------------------------
                # 9. LOAD SALES FACT TABLE
                # --------------------------------------------------

                loaded_facts = 0
                warehouse_revenue = Decimal("0.00")

                for _, item in valid_items.iterrows():
                    order = order_lookup.get(item["order_id"])

                    if order is None:
                        continue

                    customer_id = int(order["customer_id"])
                    product_id = int(item["product_id"])

                    customer = customer_lookup.loc[customer_id]

                    location_tuple = (
                        str(customer["city"])
                        if pd.notna(customer["city"]) else "",
                        str(customer["state"])
                        if pd.notna(customer["state"]) else "",
                    )

                    order_date = order["order_date"]
                    quantity = int(item["quantity"])
                    unit_price = decimal_value(item["unit_price"])
                    discount = decimal_value(item["discount"])

                    sales_amount = calculate_sales_amount(
                        quantity, unit_price, discount
                    )

                    cursor.execute(
                        """
                        INSERT INTO fact_sales
                            (order_id, customer_key, product_key, date_key,
                             location_key, quantity, unit_price, discount,
                             sales_amount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            int(item["order_id"]),
                            customer_keys[customer_id],
                            product_keys[product_id],
                            date_keys[order_date],
                            location_keys[location_tuple],
                            quantity,
                            unit_price,
                            discount,
                            sales_amount,
                        ),
                    )

                    loaded_facts += 1
                    warehouse_revenue += sales_amount

                # --------------------------------------------------
                # 10. VERIFY COUNTS BEFORE COMMIT
                # --------------------------------------------------

                cursor.execute("SELECT COUNT(*) FROM dim_customer")
                customer_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM dim_product")
                product_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM dim_location")
                location_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM dim_date")
                date_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM fact_sales")
                fact_count = cursor.fetchone()[0]

                if fact_count != loaded_facts:
                    raise RuntimeError(
                        "Fact row count does not match the number of loaded rows."
                    )

                print("\nWAREHOUSE LOAD COMPLETED SUCCESSFULLY")
                print("-" * 45)
                print(f"Customers loaded: {customer_count}")
                print(f"Products loaded: {product_count}")
                print(f"Locations loaded: {location_count}")
                print(f"Dates loaded: {date_count}")
                print(f"Fact rows loaded: {fact_count}")
                print(f"Revenue (rounded per line): {warehouse_revenue:.2f}")
                print("-" * 45)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
