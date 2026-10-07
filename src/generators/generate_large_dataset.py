import csv
import random
import uuid
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from faker import Faker

from src.ingestion.upload_to_s3 import upload_file_to_s3
from src.validation.generic_validator import validate_records


fake = Faker("en_US")
Faker.seed(42)
random.seed(42)

OUTPUT_DIR = Path("data/generated")

CUSTOMER_COUNT = 500
PRODUCT_COUNT = 100
CART_COUNT = 300
ORDER_COUNT = 500

CART_ITEMS_PER_CART = 3
ORDER_ITEMS_PER_ORDER = 3


def make_uuid(value):
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"freshmart-{value}"
        )
    )


def write_and_upload(dataset, records, fieldnames):
    result = validate_records(dataset, records)

    if result["errors"]:
        print(f"{dataset} validation FAILED")
        print(result["errors"][:10])
        raise ValueError(f"{dataset} validation failed")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"{dataset}.csv"

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(records)

    print(
        f"{dataset}: "
        f"{len(records):,} records validated"
    )

    load_date = date.today().isoformat()

    upload_file_to_s3(
        local_file=output_path,
        s3_key=(
            f"raw/{dataset}/"
            f"load_date={load_date}/"
            f"{dataset}.csv"
        )
    )


def generate_customers():
    records = []

    for i in range(1, CUSTOMER_COUNT + 1):
        number = f"FM-{100000 + i}"

        records.append({
            "customer_id": make_uuid(
                f"customer-{100000 + i}"
            ),
            "customer_number": number,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "phone": fake.phone_number(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip_code": fake.zipcode(),
            "created_at": fake.date_time_between(
                start_date="-1y",
                end_date="now"
            ).isoformat()
        })

    write_and_upload(
        "customers",
        records,
        [
            "customer_id",
            "customer_number",
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "state",
            "zip_code",
            "created_at"
        ]
    )

    return records


def generate_products():
    descriptors = [
        "Organic",
        "Fresh",
        "Premium",
        "Local",
        "Farm Fresh",
        "Sweet",
        "Crisp",
        "Ripe",
        "Select",
        "Seasonal"
    ]

    produce = [
        ("Bananas", "Fruit", "lb"),
        ("Apples", "Fruit", "lb"),
        ("Tomatoes", "Vegetables", "lb"),
        ("Spinach", "Leafy Greens", "bag"),
        ("Avocados", "Fruit", "each"),
        ("Strawberries", "Fruit", "box"),
        ("Oranges", "Fruit", "lb"),
        ("Broccoli", "Vegetables", "each"),
        ("Carrots", "Vegetables", "bag"),
        ("Grapes", "Fruit", "lb")
    ]

    records = []

    index = 1

    for descriptor in descriptors:
        for name, category, unit in produce:
            product_number = f"PRD-{100000 + index}"

            price = Decimal(
                str(
                    round(
                        random.uniform(0.99, 8.99),
                        2
                    )
                )
            )

            records.append({
                "product_id": make_uuid(
                    f"product-{product_number}"
                ),
                "product_number": product_number,
                "product_name": f"{descriptor} {name}",
                "category": category,
                "unit": unit,
                "price": str(price),
                "is_active": "true",
                "created_at": datetime.now().isoformat()
            })

            index += 1

    write_and_upload(
        "products",
        records,
        [
            "product_id",
            "product_number",
            "product_name",
            "category",
            "unit",
            "price",
            "is_active",
            "created_at"
        ]
    )

    return records


def generate_inventory(products):
    records = []

    for product in products:
        records.append({
            "inventory_id": make_uuid(
                f"inventory-{product['product_number']}"
            ),
            "product_id": product["product_id"],
            "quantity_on_hand": str(
                random.randint(20, 500)
            ),
            "reorder_level": str(
                random.randint(10, 50)
            ),
            "updated_at": datetime.now().isoformat()
        })

    write_and_upload(
        "inventory",
        records,
        [
            "inventory_id",
            "product_id",
            "quantity_on_hand",
            "reorder_level",
            "updated_at"
        ]
    )


def generate_carts(customers, products):
    carts = []
    cart_items = []

    now = datetime.now().isoformat()

    for i in range(CART_COUNT):
        cart_id = make_uuid(
            f"cart-{100001 + i}"
        )

        customer = customers[i]

        carts.append({
            "cart_id": cart_id,
            "customer_id": customer["customer_id"],
            "cart_status": random.choice([
                "active",
                "abandoned",
                "converted"
            ]),
            "created_at": now,
            "updated_at": now
        })

        selected_products = random.sample(
            products,
            CART_ITEMS_PER_CART
        )

        for item_index, product in enumerate(
            selected_products,
            start=1
        ):
            cart_items.append({
                "cart_item_id": make_uuid(
                    f"cart-item-{i}-{item_index}"
                ),
                "cart_id": cart_id,
                "product_id": product["product_id"],
                "quantity": str(
                    random.randint(1, 5)
                ),
                "unit_price": product["price"],
                "added_at": now
            })

    write_and_upload(
        "carts",
        carts,
        [
            "cart_id",
            "customer_id",
            "cart_status",
            "created_at",
            "updated_at"
        ]
    )

    write_and_upload(
        "cart_items",
        cart_items,
        [
            "cart_item_id",
            "cart_id",
            "product_id",
            "quantity",
            "unit_price",
            "added_at"
        ]
    )


def generate_orders(customers, products):
    orders = []
    order_items = []

    now = datetime.now().isoformat()

    for i in range(ORDER_COUNT):
        customer = customers[i]

        order_id = make_uuid(
            f"order-{100001 + i}"
        )

        selected_products = random.sample(
            products,
            ORDER_ITEMS_PER_ORDER
        )

        subtotal = Decimal("0.00")

        for item_index, product in enumerate(
            selected_products,
            start=1
        ):
            quantity = random.randint(1, 4)

            unit_price = Decimal(
                product["price"]
            )

            line_total = (
                unit_price *
                Decimal(quantity)
            ).quantize(
                Decimal("0.01")
            )

            subtotal += line_total

            order_items.append({
                "order_item_id": make_uuid(
                    f"order-item-{i}-{item_index}"
                ),
                "order_id": order_id,
                "product_id": product["product_id"],
                "quantity": str(quantity),
                "unit_price": str(unit_price),
                "line_total": str(line_total)
            })

        subtotal = subtotal.quantize(
            Decimal("0.01")
        )

        # Every fifth customer's first order
        # receives FIRST20.
        if i % 5 == 0:
            promo_code = "FIRST20"

            discount = (
                subtotal *
                Decimal("0.20")
            ).quantize(
                Decimal("0.01")
            )
        else:
            promo_code = ""
            discount = Decimal("0.00")

        order_total = (
            subtotal - discount
        ).quantize(
            Decimal("0.01")
        )

        orders.append({
            "order_id": order_id,
            "order_number":
                f"ORD-{100001 + i}",
            "customer_id":
                customer["customer_id"],
            "order_status":
                random.choice([
                    "completed",
                    "completed",
                    "completed",
                    "processing"
                ]),
            "promo_code":
                promo_code,
            "subtotal":
                str(subtotal),
            "discount_amount":
                str(discount),
            "order_total":
                str(order_total),
            "created_at":
                now
        })

    write_and_upload(
        "orders",
        orders,
        [
            "order_id",
            "order_number",
            "customer_id",
            "order_status",
            "promo_code",
            "subtotal",
            "discount_amount",
            "order_total",
            "created_at"
        ]
    )

    write_and_upload(
        "order_items",
        order_items,
        [
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "line_total"
        ]
    )


def main():
    print("Generating large FreshMart dataset...")
    print()

    customers = generate_customers()
    products = generate_products()

    generate_inventory(products)
    generate_carts(customers, products)
    generate_orders(customers, products)

    print()
    print("Large FreshMart dataset complete.")
    print()
    print("Expected counts:")
    print("customers:   500")
    print("products:    100")
    print("inventory:   100")
    print("carts:       300")
    print("cart_items:  900")
    print("orders:      500")
    print("order_items: 1500")


if __name__ == "__main__":
    main()