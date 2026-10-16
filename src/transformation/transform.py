import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Create processed directory if it doesn't exist
PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD SOURCE DATA
# ============================================================

def load_data():
    """
    Load all source CSV files from the sample data directory.
    """

    print("Loading source data...\n")

    customers = pd.read_csv(
        SAMPLE_DIR / "customers.csv"
    )

    products = pd.read_csv(
        SAMPLE_DIR / "products.csv"
    )

    orders = pd.read_csv(
        SAMPLE_DIR / "orders.csv"
    )

    order_items = pd.read_csv(
        SAMPLE_DIR / "order_items.csv"
    )

    payments = pd.read_csv(
        SAMPLE_DIR / "payments.csv"
    )

    print(f"Customers   : {len(customers)} records")
    print(f"Products    : {len(products)} records")
    print(f"Orders      : {len(orders)} records")
    print(f"Order Items : {len(order_items)} records")
    print(f"Payments    : {len(payments)} records")

    print("\nSource data loaded successfully!\n")

    return (
        customers,
        products,
        orders,
        order_items,
        payments
    )


# ============================================================
# CLEAN ORDER ITEMS
# ============================================================

def clean_order_items(order_items):
    """
    Clean and standardize order item data.
    """

    print("Cleaning order items...")

    # Remove duplicate rows
    order_items = order_items.drop_duplicates()

    # Convert numeric columns
    order_items["quantity"] = pd.to_numeric(
        order_items["quantity"],
        errors="coerce"
    )

    order_items["unit_price"] = pd.to_numeric(
        order_items["unit_price"],
        errors="coerce"
    )

    order_items["discount"] = pd.to_numeric(
        order_items["discount"],
        errors="coerce"
    )

    # Remove invalid records
    order_items = order_items[
        (order_items["quantity"] > 0)
        & (order_items["unit_price"] >= 0)
        & (order_items["discount"] >= 0)
        & (order_items["discount"] <= 1)
    ]

    print(
        f"Clean order items: {len(order_items)} records"
    )

    return order_items


# ============================================================
# CALCULATE ITEM REVENUE
# ============================================================

def calculate_item_revenue(order_items):
    """
    Calculate revenue for each order item.

    Formula:

    quantity × unit_price × (1 - discount)
    """

    print("\nCalculating item revenue...")

    order_items["item_revenue"] = (
        order_items["quantity"]
        * order_items["unit_price"]
        * (1 - order_items["discount"])
    ).round(2)

    return order_items


# ============================================================
# CALCULATE ORDER REVENUE
# ============================================================

def calculate_order_revenue(order_items):
    """
    Aggregate item revenue at order level.
    """

    print("Calculating order revenue...")

    order_revenue = (
        order_items
        .groupby(
            "order_id",
            as_index=False
        )["item_revenue"]
        .sum()
    )

    order_revenue.rename(
        columns={
            "item_revenue": "order_revenue"
        },
        inplace=True
    )

    # Round final revenue to 2 decimal places
    order_revenue["order_revenue"] = (
        order_revenue["order_revenue"]
        .round(2)
    )

    print(
        f"Revenue calculated for "
        f"{len(order_revenue)} orders."
    )

    return order_revenue


# ============================================================
# CREATE SALES DATASET
# ============================================================

def create_sales_dataset(
    orders,
    order_revenue
):
    """
    Combine orders with calculated revenue.
    """

    print("\nCreating sales dataset...")

    sales = orders.merge(
        order_revenue,
        on="order_id",
        how="left"
    )

    # Orders without items get revenue = 0
    sales["order_revenue"] = (
        sales["order_revenue"]
        .fillna(0)
        .round(2)
    )

    # Convert order date to datetime
    sales["order_date"] = pd.to_datetime(
        sales["order_date"],
        errors="coerce"
    )

    return sales


# ============================================================
# ADD DERIVED COLUMNS
# ============================================================

def add_derived_columns(sales):
    """
    Create additional business columns.
    """

    print("Creating derived columns...")

    # Year
    sales["order_year"] = (
        sales["order_date"]
        .dt.year
    )

    # Month
    sales["order_month"] = (
        sales["order_date"]
        .dt.month
    )

    # Month name
    sales["order_month_name"] = (
        sales["order_date"]
        .dt.strftime("%B")
    )

    # Quarter
    sales["order_quarter"] = (
        "Q"
        + sales["order_date"]
        .dt.quarter
        .astype(str)
    )

    return sales


# ============================================================
# SAVE PROCESSED DATA
# ============================================================

def save_processed_data(
    sales,
    order_items
):
    """
    Save transformed datasets to the processed layer.
    """

    sales_file = (
        PROCESSED_DIR / "sales.csv"
    )

    order_items_file = (
        PROCESSED_DIR / "order_items_processed.csv"
    )

    sales.to_csv(
        sales_file,
        index=False
    )

    order_items.to_csv(
        order_items_file,
        index=False
    )

    print("\nProcessed files created:")

    print(
        f"Sales       : {sales_file}"
    )

    print(
        f"Order Items : {order_items_file}"
    )


# ============================================================
# DISPLAY SUMMARY
# ============================================================

def display_summary(sales):
    """
    Display a small summary of the transformed data.
    """

    print("\n" + "=" * 70)
    print("TRANSFORMED DATA SAMPLE")
    print("=" * 70)

    columns_to_display = [
        "order_id",
        "customer_id",
        "order_date",
        "order_status",
        "payment_method",
        "order_revenue"
    ]

    print(
        sales[
            columns_to_display
        ].head(10).to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("TRANSFORMATION SUMMARY")
    print("=" * 70)

    print(
        f"Total Orders       : {len(sales)}"
    )

    print(
        f"Total Revenue      : "
        f"₹{sales['order_revenue'].sum():,.2f}"
    )

    print(
        f"Average Order Value: "
        f"₹{sales['order_revenue'].mean():,.2f}"
    )

    print(
        f"Maximum Order      : "
        f"₹{sales['order_revenue'].max():,.2f}"
    )

    print(
        f"Minimum Order      : "
        f"₹{sales['order_revenue'].min():,.2f}"
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("       E-COMMERCE DATA TRANSFORMATION PIPELINE")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # 1. Load data
    # --------------------------------------------------------

    (
        customers,
        products,
        orders,
        order_items,
        payments
    ) = load_data()

    # --------------------------------------------------------
    # 2. Clean order items
    # --------------------------------------------------------

    order_items = clean_order_items(
        order_items
    )

    # --------------------------------------------------------
    # 3. Calculate item-level revenue
    # --------------------------------------------------------

    order_items = calculate_item_revenue(
        order_items
    )

    # --------------------------------------------------------
    # 4. Calculate order-level revenue
    # --------------------------------------------------------

    order_revenue = calculate_order_revenue(
        order_items
    )

    # --------------------------------------------------------
    # 5. Create sales dataset
    # --------------------------------------------------------

    sales = create_sales_dataset(
        orders,
        order_revenue
    )

    # --------------------------------------------------------
    # 6. Add business columns
    # --------------------------------------------------------

    sales = add_derived_columns(
        sales
    )

    # --------------------------------------------------------
    # 7. Save processed data
    # --------------------------------------------------------

    save_processed_data(
        sales,
        order_items
    )

    # --------------------------------------------------------
    # 8. Display summary
    # --------------------------------------------------------

    display_summary(
        sales
    )

    print("\n")
    print("=" * 70)
    print("Transformation completed successfully!")
    print("=" * 70)
    print()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()