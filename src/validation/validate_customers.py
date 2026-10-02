import uuid


REQUIRED_FIELDS = [
    "customer_id",
    "customer_number",
    "first_name",
    "last_name",
    "email",
    "created_at",
]


def validate_customer(customer):
    errors = []

    # Check 1: Required fields
    for field in REQUIRED_FIELDS:
        if not customer.get(field):
            errors.append(f"Missing required field: {field}")

    # Check 2: Valid UUID
    customer_id = customer.get("customer_id")

    if customer_id:
        try:
            uuid.UUID(customer_id)
        except ValueError:
            errors.append("Invalid customer_id UUID")

    # Check 3: Email contains basic required structure
    email = customer.get("email")

    if email and ("@" not in email or "." not in email):
        errors.append("Invalid email format")

    return errors

def validate_customers(customers):
    all_errors = []

    seen_customer_ids = set()
    seen_customer_numbers = set()

    for row_number, customer in enumerate(customers, start=1):
        # Run the individual customer checks
        row_errors = validate_customer(customer)

        for error in row_errors:
            all_errors.append(
                f"Row {row_number}: {error}"
            )

        # Check duplicate customer_id
        customer_id = customer.get("customer_id")

        if customer_id:
            if customer_id in seen_customer_ids:
                all_errors.append(
                    f"Row {row_number}: Duplicate customer_id: {customer_id}"
                )
            else:
                seen_customer_ids.add(customer_id)

        # Check duplicate customer_number
        customer_number = customer.get("customer_number")

        if customer_number:
            if customer_number in seen_customer_numbers:
                all_errors.append(
                    f"Row {row_number}: Duplicate customer_number: {customer_number}"
                )
            else:
                seen_customer_numbers.add(customer_number)

    return all_errors

