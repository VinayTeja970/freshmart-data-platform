import csv
import uuid
from pathlib import Path

from faker import Faker

from src.validation.validate_customers import validate_customers

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
validation_errors = validate_customers(customers)

if validation_errors:
    print("Customer validation FAILED:")

    for error in validation_errors:
        print(f" - {error}")

    raise SystemExit(1)

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