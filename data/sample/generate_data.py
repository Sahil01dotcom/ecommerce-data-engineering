import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = Path(__file__).parent

random.seed(42)

NUM_CUSTOMERS = 100
NUM_PRODUCTS = 50
NUM_ORDERS = 500


# ============================================================
# MASTER DATA
# ============================================================

FIRST_NAMES = [
    "Rahul",
    "Amit",
    "Priya",
    "Sneha",
    "Rohan",
    "Neha",
    "Akash",
    "Pooja",
    "Vikas",
    "Anjali"
]


LAST_NAMES = [
    "Sharma",
    "Patil",
    "Kulkarni",
    "Deshmukh",
    "Joshi",
    "Pawar",
    "Fulsundar",
    "More"
]


CITIES = [
    ("Pune", "Maharashtra"),
    ("Mumbai", "Maharashtra"),
    ("Bangalore", "Karnataka"),
    ("Hyderabad", "Telangana"),
    ("Chennai", "Tamil Nadu"),
    ("Delhi", "Delhi"),
    ("Noida", "Uttar Pradesh"),
    ("Ahmedabad", "Gujarat")
]


PRODUCT_CATEGORIES = [
    "Electronics",
    "Fashion",
    "Home & Kitchen",
    "Beauty",
    "Sports"
]


PRODUCT_NAMES = [
    "Laptop",
    "Smartphone",
    "Headphones",
    "Keyboard",
    "Mouse",
    "Monitor",
    "T-Shirt",
    "Jeans",
    "Shoes",
    "Backpack",
    "Mixer Grinder",
    "Air Fryer",
    "Coffee Maker",
    "Face Wash",
    "Perfume",
    "Yoga Mat",
    "Running Shoes",
    "Dumbbells"
]


PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Cash on Delivery"
]


ORDER_STATUSES = [
    "Delivered",
    "Shipped",
    "Processing",
    "Cancelled"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date(start_date, end_date):
    """Generate a random date between two dates."""

    delta = end_date - start_date

    random_days = random.randint(
        0,
        delta.days
    )

    return start_date + timedelta(
        days=random_days
    )


def write_csv(
    filename,
    fieldnames,
    rows
):
    """Write records to a CSV file."""

    filepath = OUTPUT_DIR / filename

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Created: {filepath}"
    )


# ============================================================
# GENERATE CUSTOMERS
# ============================================================

def generate_customers():

    customers = []

    for customer_id in range(
        1,
        NUM_CUSTOMERS + 1
    ):

        first_name = random.choice(
            FIRST_NAMES
        )

        last_name = random.choice(
            LAST_NAMES
        )

        city, state = random.choice(
            CITIES
        )

        customers.append({

            "customer_id": customer_id,

            "first_name": first_name,

            "last_name": last_name,

            "email":
                f"{first_name.lower()}."
                f"{last_name.lower()}"
                f"{customer_id}"
                "@example.com",

            "city": city,

            "state": state,

            "signup_date":
                random_date(
                    datetime(2024, 1, 1),
                    datetime(2025, 12, 31)
                ).date()
        })

    write_csv(
        "customers.csv",

        [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "city",
            "state",
            "signup_date"
        ],

        customers
    )


# ============================================================
# GENERATE PRODUCTS
# ============================================================

def generate_products():

    products = []

    for product_id in range(
        1,
        NUM_PRODUCTS + 1
    ):

        category = random.choice(
            PRODUCT_CATEGORIES
        )

        product_name = random.choice(
            PRODUCT_NAMES
        )

        # Generate realistic prices
        if category == "Electronics":

            price = random.uniform(
                1000,
                100000
            )

        elif category == "Fashion":

            price = random.uniform(
                500,
                10000
            )

        elif category == "Home & Kitchen":

            price = random.uniform(
                500,
                30000
            )

        elif category == "Beauty":

            price = random.uniform(
                200,
                5000
            )

        else:

            price = random.uniform(
                500,
                15000
            )

        products.append({

            "product_id":
                product_id,

            "product_name":
                product_name,

            "category":
                category,

            "price":
                round(price, 2),

            "stock_quantity":
                random.randint(
                    10,
                    500
                )
        })

    write_csv(
        "products.csv",

        [
            "product_id",
            "product_name",
            "category",
            "price",
            "stock_quantity"
        ],

        products
    )

    return products


# ============================================================
# GENERATE ORDERS
# ============================================================

def generate_orders():

    orders = []

    start_date = datetime(
        2025,
        1,
        1
    )

    end_date = datetime(
        2025,
        12,
        31
    )

    for order_id in range(
        1,
        NUM_ORDERS + 1
    ):

        orders.append({

            "order_id":
                order_id,

            "customer_id":
                random.randint(
                    1,
                    NUM_CUSTOMERS
                ),

            "order_date":
                random_date(
                    start_date,
                    end_date
                ).date(),

            "order_status":
                random.choices(

                    ORDER_STATUSES,

                    weights=[
                        50,   # Delivered
                        25,   # Shipped
                        20,   # Processing
                        5     # Cancelled
                    ],

                    k=1
                )[0],

            "payment_method":
                random.choice(
                    PAYMENT_METHODS
                )
        })

    write_csv(
        "orders.csv",

        [
            "order_id",
            "customer_id",
            "order_date",
            "order_status",
            "payment_method"
        ],

        orders
    )

    return orders


# ============================================================
# GENERATE ORDER ITEMS
# ============================================================

def generate_order_items(
    orders,
    products
):

    order_items = []

    item_id = 1

    # Product lookup for prices
    product_lookup = {
        product["product_id"]:
            product["price"]

        for product in products
    }

    for order in orders:

        order_id = order["order_id"]

        order_status = order["order_status"]

        # ----------------------------------------------------
        # Cancelled orders are not billable.
        # Therefore we don't create order items for them.
        # ----------------------------------------------------

        if order_status == "Cancelled":

            continue

        number_of_items = random.randint(
            1,
            4
        )

        selected_products = random.sample(

            range(
                1,
                NUM_PRODUCTS + 1
            ),

            number_of_items
        )

        for product_id in selected_products:

            quantity = random.randint(
                1,
                5
            )

            # Use the actual product price
            unit_price = product_lookup[
                product_id
            ]

            discount = round(
                random.uniform(
                    0,
                    0.30
                ),
                2
            )

            order_items.append({

                "order_item_id":
                    item_id,

                "order_id":
                    order_id,

                "product_id":
                    product_id,

                "quantity":
                    quantity,

                "unit_price":
                    round(
                        unit_price,
                        2
                    ),

                "discount":
                    discount
            })

            item_id += 1

    write_csv(
        "order_items.csv",

        [
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "discount"
        ],

        order_items
    )

    return order_items


# ============================================================
# CALCULATE ORDER TOTALS
# ============================================================

def calculate_order_totals(
    orders,
    order_items
):

    order_totals = {}

    for item in order_items:

        order_id = item["order_id"]

        quantity = item["quantity"]

        unit_price = item["unit_price"]

        discount = item["discount"]

        item_total = (
            quantity
            * unit_price
            * (1 - discount)
        )

        item_total = round(
            item_total,
            2
        )

        if order_id not in order_totals:

            order_totals[order_id] = 0.0

        order_totals[order_id] += item_total

    # Round final order totals
    for order_id in order_totals:

        order_totals[order_id] = round(
            order_totals[order_id],
            2
        )

    # Cancelled orders have zero revenue
    for order in orders:

        order_id = order["order_id"]

        if order["order_status"] == "Cancelled":

            order_totals[order_id] = 0.0

        elif order_id not in order_totals:

            order_totals[order_id] = 0.0

    return order_totals


# ============================================================
# GENERATE PAYMENTS
# ============================================================

def generate_payments(
    orders,
    order_totals
):

    payments = []

    for order in orders:

        order_id = order["order_id"]

        order_status = order["order_status"]

        order_total = order_totals[
            order_id
        ]

        # ----------------------------------------------------
        # Cancelled orders
        # ----------------------------------------------------

        if order_status == "Cancelled":

            payment_status = "Failed"

            payment_amount = 0.0

        # ----------------------------------------------------
        # Active orders
        # ----------------------------------------------------

        else:

            payment_status = "Success"

            payment_amount = order_total

        payments.append({

            "payment_id":
                order_id,

            "order_id":
                order_id,

            "payment_amount":
                round(
                    payment_amount,
                    2
                ),

            "payment_status":
                payment_status
        })

    write_csv(
        "payments.csv",

        [
            "payment_id",
            "order_id",
            "payment_amount",
            "payment_status"
        ],

        payments
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("       E-COMMERCE DATASET GENERATOR")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # 1. Customers
    # --------------------------------------------------------

    generate_customers()

    # --------------------------------------------------------
    # 2. Products
    # --------------------------------------------------------

    products = generate_products()

    # --------------------------------------------------------
    # 3. Orders
    # --------------------------------------------------------

    orders = generate_orders()

    # --------------------------------------------------------
    # 4. Order Items
    # --------------------------------------------------------

    order_items = generate_order_items(
        orders,
        products
    )

    # --------------------------------------------------------
    # 5. Calculate Order Totals
    # --------------------------------------------------------

    order_totals = calculate_order_totals(
        orders,
        order_items
    )

    # --------------------------------------------------------
    # 6. Payments
    # --------------------------------------------------------

    generate_payments(
        orders,
        order_totals
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    cancelled_orders = sum(

        1

        for order in orders

        if order["order_status"]
        == "Cancelled"
    )

    successful_payments = sum(

        1

        for order in orders

        if order["order_status"]
        != "Cancelled"
    )

    print()
    print("=" * 70)
    print("DATASET SUMMARY")
    print("=" * 70)

    print(
        f"Customers          : {NUM_CUSTOMERS}"
    )

    print(
        f"Products           : {NUM_PRODUCTS}"
    )

    print(
        f"Orders             : {NUM_ORDERS}"
    )

    print(
        f"Order Items        : {len(order_items)}"
    )

    print(
        f"Cancelled Orders   : {cancelled_orders}"
    )

    print(
        f"Successful Payments: {successful_payments}"
    )

    print()
    print(
        "Dataset generation completed successfully!"
    )
    print("=" * 70)
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()