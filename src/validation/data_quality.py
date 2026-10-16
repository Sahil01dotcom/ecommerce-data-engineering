import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "sample"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """Load all source and processed datasets."""

    customers = pd.read_csv(
        DATA_DIR / "customers.csv"
    )

    products = pd.read_csv(
        DATA_DIR / "products.csv"
    )

    orders = pd.read_csv(
        DATA_DIR / "orders.csv"
    )

    order_items = pd.read_csv(
        DATA_DIR / "order_items.csv"
    )

    payments = pd.read_csv(
        DATA_DIR / "payments.csv"
    )

    sales = pd.read_csv(
        PROCESSED_DIR / "sales.csv"
    )

    return (
        customers,
        products,
        orders,
        order_items,
        payments,
        sales
    )


# ============================================================
# RESULT TRACKING
# ============================================================

passed_checks = 0
failed_checks = 0
warning_checks = 0


def print_pass(message):
    global passed_checks

    passed_checks += 1

    print(f"  [PASS] {message}")


def print_fail(message):
    global failed_checks

    failed_checks += 1

    print(f"  [FAIL] {message}")


def print_warning(message):
    global warning_checks

    warning_checks += 1

    print(f"  [WARN] {message}")


# ============================================================
# PRIMARY KEY CHECK
# ============================================================

def check_primary_key(df, column, table_name):
    """Check that a column contains unique and non-null values."""

    null_count = df[column].isna().sum()
    duplicate_count = df[column].duplicated().sum()

    if null_count == 0 and duplicate_count == 0:

        print_pass(
            f"{table_name}.{column} is unique and non-null"
        )

    else:

        print_fail(
            f"{table_name}.{column}: "
            f"{null_count} NULLs, "
            f"{duplicate_count} duplicates"
        )


# ============================================================
# NULL CHECK
# ============================================================

def check_null_values(df, table_name, columns):
    """Check required columns for NULL values."""

    for column in columns:

        null_count = df[column].isna().sum()

        if null_count == 0:

            print_pass(
                f"{table_name}.{column} has no NULL values"
            )

        else:

            print_fail(
                f"{table_name}.{column} contains "
                f"{null_count} NULL values"
            )


# ============================================================
# DUPLICATE ROW CHECK
# ============================================================

def check_duplicates(df, table_name):
    """Check for completely duplicated rows."""

    duplicate_count = df.duplicated().sum()

    if duplicate_count == 0:

        print_pass(
            f"{table_name} contains no duplicate rows"
        )

    else:

        print_fail(
            f"{table_name} contains "
            f"{duplicate_count} duplicate rows"
        )


# ============================================================
# FOREIGN KEY CHECK
# ============================================================

def check_foreign_key(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship
):
    """
    Check whether child-table keys exist
    in the parent table.
    """

    invalid_values = (
        child_df[
            ~child_df[child_column].isin(
                parent_df[parent_column]
            )
        ][child_column]
        .dropna()
        .unique()
    )

    if len(invalid_values) == 0:

        print_pass(
            f"{relationship} is valid"
        )

    else:

        print_fail(
            f"{relationship}: "
            f"{len(invalid_values)} invalid keys"
        )


# ============================================================
# ORDER ITEM BUSINESS RULES
# ============================================================

def check_order_items(order_items):
    """Validate order-item business rules."""

    # Quantity must be greater than zero
    invalid_quantity = (
        order_items["quantity"] <= 0
    ).sum()

    if invalid_quantity == 0:

        print_pass(
            "All order quantities are greater than zero"
        )

    else:

        print_fail(
            f"{invalid_quantity} order items "
            f"have invalid quantities"
        )

    # Unit price cannot be negative
    invalid_price = (
        order_items["unit_price"] < 0
    ).sum()

    if invalid_price == 0:

        print_pass(
            "All unit prices are valid"
        )

    else:

        print_fail(
            f"{invalid_price} order items "
            f"have negative prices"
        )

    # Discount must be between 0 and 1
    invalid_discount = (
        (order_items["discount"] < 0)
        |
        (order_items["discount"] > 1)
    ).sum()

    if invalid_discount == 0:

        print_pass(
            "All discounts are between 0 and 100%"
        )

    else:

        print_fail(
            f"{invalid_discount} order items "
            f"have invalid discounts"
        )


# ============================================================
# ORDER STATUS CHECK
# ============================================================

def check_order_status(orders):
    """Validate order status values."""

    valid_statuses = {
        "Delivered",
        "Shipped",
        "Processing",
        "Cancelled"
    }

    invalid_statuses = set(
        orders["order_status"].dropna().unique()
    ) - valid_statuses

    if not invalid_statuses:

        print_pass(
            "All order statuses are valid"
        )

    else:

        print_fail(
            f"Invalid order statuses: "
            f"{invalid_statuses}"
        )


# ============================================================
# PAYMENT STATUS CHECK
# ============================================================

def check_payment_status(payments):
    """Validate payment status values."""

    valid_statuses = {
        "Success",
        "Failed"
    }

    invalid_statuses = set(
        payments["payment_status"].dropna().unique()
    ) - valid_statuses

    if not invalid_statuses:

        print_pass(
            "All payment statuses are valid"
        )

    else:

        print_fail(
            f"Invalid payment statuses: "
            f"{invalid_statuses}"
        )


# ============================================================
# REVENUE VALIDATION
# ============================================================

def check_revenue(order_items, sales):
    """
    Recalculate revenue independently and compare
    against the processed sales dataset.
    """

    expected_revenue = (
        order_items["quantity"]
        * order_items["unit_price"]
        * (1 - order_items["discount"])
    ).round(2)

    validation_df = order_items.copy()

    validation_df["expected_item_revenue"] = (
        expected_revenue
    )

    expected_order_revenue = (
        validation_df
        .groupby("order_id")[
            "expected_item_revenue"
        ]
        .sum()
        .round(2)
        .reset_index()
    )

    comparison = sales.merge(
        expected_order_revenue,
        on="order_id",
        how="left"
    )

    comparison[
        "expected_item_revenue"
    ] = comparison[
        "expected_item_revenue"
    ].fillna(0).round(2)

    comparison["revenue_difference"] = (
        comparison["order_revenue"]
        - comparison["expected_item_revenue"]
    ).round(2)

    mismatches = comparison[
        comparison["revenue_difference"].abs() > 0.01
    ]

    if len(mismatches) == 0:

        print_pass(
            "Processed revenue matches source "
            "order-item calculations"
        )

    else:

        print_fail(
            f"{len(mismatches)} orders have "
            f"revenue calculation mismatches"
        )


# ============================================================
# PAYMENT RECONCILIATION
# ============================================================

def check_payment_reconciliation(
    payments,
    sales
):
    """
    Compare successful payment amounts with
    calculated order revenue.

    NOTE:
    Our sample payment data was intentionally generated
    independently from order_items. Therefore mismatches
    are expected at this stage.
    """

    successful_payments = payments[
        payments["payment_status"] == "Success"
    ]

    payment_totals = (
        successful_payments
        .groupby("order_id")["payment_amount"]
        .sum()
        .reset_index()
    )

    payment_totals.rename(
        columns={
            "payment_amount": "paid_amount"
        },
        inplace=True
    )

    comparison = sales.merge(
        payment_totals,
        on="order_id",
        how="left"
    )

    comparison["paid_amount"] = (
        comparison["paid_amount"]
        .fillna(0)
        .round(2)
    )

    comparison["payment_difference"] = (
        comparison["paid_amount"]
        - comparison["order_revenue"]
    ).round(2)

    mismatches = comparison[
        comparison["payment_difference"].abs() > 0.01
    ]

    if len(mismatches) == 0:

        print_pass(
            "Payment amounts reconcile with order revenue"
        )

    else:

        print_warning(
            f"{len(mismatches)} orders have payment "
            f"reconciliation differences"
        )

        print(
            "       This is expected because our "
            "sample payment data was generated independently."
        )


# ============================================================
# MAIN DATA QUALITY PIPELINE
# ============================================================

def run_data_quality_checks():

    global passed_checks
    global failed_checks
    global warning_checks

    passed_checks = 0
    failed_checks = 0
    warning_checks = 0

    print("\n")
    print("=" * 70)
    print("             DATA QUALITY VALIDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    (
        customers,
        products,
        orders,
        order_items,
        payments,
        sales
    ) = load_data()

    # --------------------------------------------------------
    # 1. Primary Key Checks
    # --------------------------------------------------------

    print("\n[1] PRIMARY KEY CHECKS")
    print("-" * 70)

    check_primary_key(
        customers,
        "customer_id",
        "customers"
    )

    check_primary_key(
        products,
        "product_id",
        "products"
    )

    check_primary_key(
        orders,
        "order_id",
        "orders"
    )

    check_primary_key(
        order_items,
        "order_item_id",
        "order_items"
    )

    check_primary_key(
        payments,
        "payment_id",
        "payments"
    )

    # --------------------------------------------------------
    # 2. NULL Checks
    # --------------------------------------------------------

    print("\n[2] NULL VALUE CHECKS")
    print("-" * 70)

    check_null_values(
        customers,
        "customers",
        [
            "customer_id",
            "email",
            "signup_date"
        ]
    )

    check_null_values(
        products,
        "products",
        [
            "product_id",
            "product_name",
            "price"
        ]
    )

    check_null_values(
        orders,
        "orders",
        [
            "order_id",
            "customer_id",
            "order_date"
        ]
    )

    check_null_values(
        order_items,
        "order_items",
        [
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price"
        ]
    )

    check_null_values(
        payments,
        "payments",
        [
            "payment_id",
            "order_id",
            "payment_amount"
        ]
    )

    # --------------------------------------------------------
    # 3. Duplicate Checks
    # --------------------------------------------------------

    print("\n[3] DUPLICATE CHECKS")
    print("-" * 70)

    check_duplicates(
        customers,
        "customers"
    )

    check_duplicates(
        products,
        "products"
    )

    check_duplicates(
        orders,
        "orders"
    )

    check_duplicates(
        order_items,
        "order_items"
    )

    check_duplicates(
        payments,
        "payments"
    )

    # --------------------------------------------------------
    # 4. Foreign Key Checks
    # --------------------------------------------------------

    print("\n[4] FOREIGN KEY CHECKS")
    print("-" * 70)

    check_foreign_key(
        orders,
        "customer_id",
        customers,
        "customer_id",
        "orders.customer_id → customers.customer_id"
    )

    check_foreign_key(
        order_items,
        "order_id",
        orders,
        "order_id",
        "order_items.order_id → orders.order_id"
    )

    check_foreign_key(
        order_items,
        "product_id",
        products,
        "product_id",
        "order_items.product_id → products.product_id"
    )

    check_foreign_key(
        payments,
        "order_id",
        orders,
        "order_id",
        "payments.order_id → orders.order_id"
    )

    # --------------------------------------------------------
    # 5. Business Rules
    # --------------------------------------------------------

    print("\n[5] BUSINESS RULE CHECKS")
    print("-" * 70)

    check_order_items(
        order_items
    )

    check_order_status(
        orders
    )

    check_payment_status(
        payments
    )

    # --------------------------------------------------------
    # 6. Revenue Validation
    # --------------------------------------------------------

    print("\n[6] REVENUE VALIDATION")
    print("-" * 70)

    check_revenue(
        order_items,
        sales
    )

    # --------------------------------------------------------
    # 7. Payment Reconciliation
    # --------------------------------------------------------

    print("\n[7] PAYMENT RECONCILIATION")
    print("-" * 70)

    check_payment_reconciliation(
        payments,
        sales
    )

    # --------------------------------------------------------
    # Final Summary
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("                 QUALITY SUMMARY")
    print("=" * 70)

    print(
        f"Passed Checks   : {passed_checks}"
    )

    print(
        f"Failed Checks   : {failed_checks}"
    )

    print(
        f"Warnings        : {warning_checks}"
    )

    print("=" * 70)

    if failed_checks == 0:

        print(
            "\nDATA QUALITY CHECKS PASSED!"
        )

    else:

        print(
            "\nDATA QUALITY CHECKS FAILED!"
        )

    print()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_data_quality_checks()