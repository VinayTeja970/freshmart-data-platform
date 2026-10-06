import csv
import uuid
from datetime import date, datetime
from pathlib import Path

from src.ingestion.upload_to_s3 import upload_file_to_s3
from src.validation.generic_validator import validate_records


PRODUCTS = [
    {
        "product_number": "PRD-100001",
        "product_name": "Organic Bananas",
        "category": "Fruit",
        "unit": "lb",
        "price": "1.29",
        "is_active": "true"
    },
    {
        "product_number": "PRD-100002",
        "product_name": "Honeycrisp Apples",
        "category": "Fruit",
        "unit": "lb",
        "price": "2.49",
        "is_active": "true"
    },
    {
        "product_number": "PRD-100003",
        "product_name": "Roma Tomatoes",
        "category": "Vegetables",
        "unit": "lb",
        "price": "1.79",
        "is_active": "true"
    },
    {
        "product_number": "PRD-100004",
        "product_name": "Baby Spinach",
        "category": "Leafy Greens",
        "unit": "bag",
        "price": "3.99",
        "is_active": "true"
    },
    {
        "product_number": "PRD-100005",
        "product_name": "Avocados",
        "category": "Fruit",
        "unit": "each",
        "price": "1.49",
        "is_active": "true"
    }
]


def generate_products():
    output_path = Path("data/generated/products.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    created_at = datetime.now().isoformat()

    records = []

    for product in PRODUCTS:
        record = {
            "product_id": str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"freshmart-product-{product['product_number']}"
                )
            ),
            "product_number": product["product_number"],
            "product_name": product["product_name"],
            "category": product["category"],
            "unit": product["unit"],
            "price": product["price"],
            "is_active": product["is_active"],
            "created_at": created_at
        }

        records.append(record)

    result = validate_records("products", records)

    if result["errors"]:
        print("Product validation FAILED")

        for error in result["errors"]:
            print(error)

        raise ValueError("Product validation failed")

    print("Product validation PASSED")

    fieldnames = [
        "product_id",
        "product_number",
        "product_name",
        "category",
        "unit",
        "price",
        "is_active",
        "created_at"
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} products")
    print(f"Saved to: {output_path}")

    load_date = date.today().isoformat()

    s3_key = (
        f"raw/products/"
        f"load_date={load_date}/"
        f"products.csv"
    )

    upload_file_to_s3(
        local_file=output_path,
        s3_key=s3_key
    )


if __name__ == "__main__":
    generate_products()