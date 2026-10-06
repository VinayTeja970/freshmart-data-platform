import csv
import uuid
from pathlib import Path

from faker import Faker
from datetime import date

from src.validation.generic_validator import validate_records

from src.ingestion.upload_to_s3 import upload_file_to_s3

fake = Faker("en_US")
Faker.seed(42)

# Create an empty list BEFORE the loop
customers = []

for i in range(5):
    customer_id = str(
        uuid.uuid5(uuid.NAMESPACE_DNS, f"freshmart-customer-{100001 + i}")
    )
    customer_number = f"FM-{100001 + i}"

    customer = {
        "customer_id": customer_id,
        "customer_number": customer_number,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip_code": fake.zipcode(),
        "created_at": fake.date_time_between(
            start_date="-1y",
            end_date="now"
        ).isoformat()
    }

    customers.append(customer)


#Validate before writing
result = validate_records("customers", customers)

if result["errors"]:
    print("Customer validation FAILED")

    for error in result["errors"]:
        print(error)

    raise ValueError("Customer validation failed")

print("Customer validation PASSED")

output_path = Path("data/generated/customers.csv")

with output_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=customers[0].keys()
    )

    writer.writeheader()
    writer.writerows(customers)

print(f"Generated {len(customers)} customers")
print(f"Saved to: {output_path}")

load_date = date.today().isoformat()

s3_key = (
    f"raw/customers/"
    f"load_date={load_date}/"
    f"customers.csv"
)

upload_file_to_s3(
    local_file=output_path,
    s3_key=s3_key
)