import csv
import uuid
from datetime import date, datetime
from pathlib import Path
from decimal import Decimal

from src.ingestion.upload_to_s3 import upload_file_to_s3
from src.validation.generic_validator import validate_records


OUTPUT_DIR = Path("data/generated")


def customer_id(customer_number):
    numeric_part = int(customer_number.split("-")[1])

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"freshmart-customer-{numeric_part}"
        )
    )


def product_id(product_number):
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"freshmart-product-{product_number}"
        )
    )


def deterministic_uuid(value):
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"freshmart-{value}"
        )
    )


def write_and_upload(dataset, records, fieldnames):
    result = validate_records(
        dataset,
        records
    )

    if result["errors"]:
        print(f"{dataset} validation FAILED")

        for error in result["errors"]:
            print(error)

        raise ValueError(
            f"{dataset} validation failed"
        )

    print(f"{dataset} validation PASSED")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        OUTPUT_DIR /
        f"{dataset}.csv"
    )

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
        f"Generated {len(records)} "
        f"{dataset} records"
    )

    load_date = date.today().isoformat()

    s3_key = (
        f"raw/{dataset}/"
        f"load_date={load_date}/"
        f"{dataset}.csv"
    )

    upload_file_to_s3(
        local_file=output_path,
        s3_key=s3_key
    )


def generate_inventory(now):
    products = [
        ("PRD-100001", 120, 25),
        ("PRD-100002", 85, 20),
        ("PRD-100003", 70, 15),
        ("PRD-100004", 42, 10),
        ("PRD-100005", 95, 20)
    ]

    records = []

    for product_number, quantity, reorder_level in products:
        pid = product_id(product_number)

        records.append({
            "inventory_id": deterministic_uuid(
                f"inventory-{product_number}"
            ),
            "product_id": pid,
            "quantity_on_hand": str(quantity),
            "reorder_level": str(reorder_level),
            "updated_at": now
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


def generate_carts(now):
    carts = [
        ("cart-100001", "FM-100001", "converted"),
        ("cart-100002", "FM-100002", "active"),
        ("cart-100003", "FM-100003", "converted")
    ]

    records = []

    for cart_key, customer_number, status in carts:
        records.append({
            "cart_id": deterministic_uuid(cart_key),
            "customer_id": customer_id(
                customer_number
            ),
            "cart_status": status,
            "created_at": now,
            "updated_at": now
        })

    write_and_upload(
        "carts",
        records,
        [
            "cart_id",
            "customer_id",
            "cart_status",
            "created_at",
            "updated_at"
        ]
    )


def generate_cart_items(now):
    items = [
        (
            "cart-item-100001",
            "cart-100001",
            "PRD-100001",
            2,
            "1.29"
        ),
        (
            "cart-item-100002",
            "cart-100001",
            "PRD-100005",
            3,
            "1.49"
        ),
        (
            "cart-item-100003",
            "cart-100002",
            "PRD-100004",
            1,
            "3.99"
        ),
        (
            "cart-item-100004",
            "cart-100003",
            "PRD-100002",
            2,
            "2.49"
        )
    ]

    records = []

    for (
        item_key,
        cart_key,
        product_number,
        quantity,
        unit_price
    ) in items:

        records.append({
            "cart_item_id":
                deterministic_uuid(item_key),

            "cart_id":
                deterministic_uuid(cart_key),

            "product_id":
                product_id(product_number),

            "quantity":
                str(quantity),

            "unit_price":
                unit_price,

            "added_at":
                now
        })

    write_and_upload(
        "cart_items",
        records,
        [
            "cart_item_id",
            "cart_id",
            "product_id",
            "quantity",
            "unit_price",
            "added_at"
        ]
    )


def generate_orders(now):
    orders = []

    order_1_subtotal = Decimal("7.05")
    order_1_discount = Decimal("1.41")

    orders.append({
        "order_id":
            deterministic_uuid("order-100001"),

        "order_number":
            "ORD-100001",

        "customer_id":
            customer_id("FM-100001"),

        "order_status":
            "completed",

        "promo_code":
            "FIRST20",

        "subtotal":
            str(order_1_subtotal),

        "discount_amount":
            str(order_1_discount),

        "order_total":
            str(
                order_1_subtotal -
                order_1_discount
            ),

        "created_at":
            now
    })

    order_2_subtotal = Decimal("4.98")

    orders.append({
        "order_id":
            deterministic_uuid("order-100002"),

        "order_number":
            "ORD-100002",

        "customer_id":
            customer_id("FM-100003"),

        "order_status":
            "completed",

        "promo_code":
            "",

        "subtotal":
            str(order_2_subtotal),

        "discount_amount":
            "0.00",

        "order_total":
            str(order_2_subtotal),

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


def generate_order_items():
    items = [
        (
            "order-item-100001",
            "order-100001",
            "PRD-100001",
            2,
            Decimal("1.29")
        ),
        (
            "order-item-100002",
            "order-100001",
            "PRD-100005",
            3,
            Decimal("1.49")
        ),
        (
            "order-item-100003",
            "order-100002",
            "PRD-100002",
            2,
            Decimal("2.49")
        )
    ]

    records = []

    for (
        item_key,
        order_key,
        product_number,
        quantity,
        unit_price
    ) in items:

        line_total = (
            Decimal(quantity) *
            unit_price
        )

        records.append({
            "order_item_id":
                deterministic_uuid(item_key),

            "order_id":
                deterministic_uuid(order_key),

            "product_id":
                product_id(product_number),

            "quantity":
                str(quantity),

            "unit_price":
                str(unit_price),

            "line_total":
                str(line_total)
        })

    write_and_upload(
        "order_items",
        records,
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
    now = datetime.now().isoformat()

    generate_inventory(now)
    generate_carts(now)
    generate_cart_items(now)
    generate_orders(now)
    generate_order_items()

    print()
    print(
        "All remaining FreshMart datasets "
        "generated and uploaded."
    )


if __name__ == "__main__":
    main()