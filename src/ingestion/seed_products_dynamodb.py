import csv
from pathlib import Path
from decimal import Decimal

import boto3


TABLE_NAME = "freshmart-products"
PRODUCTS_FILE = Path("data/generated/products.csv")


def seed_products():
    if not PRODUCTS_FILE.exists():
        raise FileNotFoundError(
            f"Products file not found: {PRODUCTS_FILE}"
        )

    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1"
    )

    table = dynamodb.Table(TABLE_NAME)

    with PRODUCTS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        products = list(reader)

    print(f"Found {len(products)} products")

    for product in products:
        item = {
            "product_id": product["product_id"],
            "product_number": product["product_number"],
            "product_name": product["product_name"],
            "category": product["category"],
            "unit": product["unit"],
            "price": Decimal(product["price"]),
            "is_active":
                product["is_active"].lower() == "true",
            "created_at": product["created_at"]
        }

        table.put_item(
            Item=item
        )

        print(
            f"Inserted "
            f"{product['product_number']} - "
            f"{product['product_name']}"
        )

    print("DynamoDB product seeding completed")


if __name__ == "__main__":
    seed_products()