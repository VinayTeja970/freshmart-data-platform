import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation

from src.config.dataset_config import DATASETS

def validate_records(dataset, records):
    """
    Validate records using the rules defined for a dataset.

    Returns:
        {
            "valid_records": [...],
            "errors": [...]
        }
    """

    if dataset not in DATASETS:
        raise ValueError(f"Unsupported dataset: {dataset}")

    config = DATASETS[dataset]

    required_fields = config.get("required_fields", [])
    uuid_fields = config.get("uuid_fields", [])
    email_fields = config.get("email_fields", [])
    decimal_fields = config.get("decimal_fields", [])
    boolean_fields = config.get("boolean_fields", [])
    timestamp_fields = config.get("timestamp_fields", [])
    integer_fields = config.get("integer_fields", [])

    primary_key = config.get("primary_key")
    business_key = config.get("business_key")

    valid_records = []
    errors = []

    seen_primary_keys = set()
    seen_business_keys = set()

    for row_number, record in enumerate(records, start=1):
        row_errors = []

        # Required fields
        for field in required_fields:
            value = record.get(field)

            if value is None or str(value).strip() == "":
                row_errors.append(
                    f"missing required field '{field}'"
                )

        # UUID validation
        for field in uuid_fields:
            value = record.get(field)

            if value:
                try:
                    uuid.UUID(str(value))
                except ValueError:
                    row_errors.append(
                        f"invalid UUID in field '{field}': {value}"
                    )

        # Basic email validation
        for field in email_fields:
            value = record.get(field)

            if value:
                email = str(value).strip()

                if "@" not in email or "." not in email.split("@")[-1]:
                    row_errors.append(
                        f"invalid email in field '{field}': {value}"
                    )
        # Decimal validation
        for field in decimal_fields:
            value = record.get(field)

            if value:
                try:
                    Decimal(str(value))
                except InvalidOperation:
                    row_errors.append(
                        f"invalid decimal in field '{field}': {value}"
                    )


        # Boolean validation
        for field in boolean_fields:
            value = record.get(field)

            if value:
                normalized_value = str(value).strip().lower()

                valid_boolean_values = {
                    "true",
                    "false",
                    "1",
                    "0"
                }

                if normalized_value not in valid_boolean_values:
                    row_errors.append(
                        f"invalid boolean in field '{field}': {value}"
                    )


        # Timestamp validation
        for field in timestamp_fields:
            value = record.get(field)

            if value:
                try:
                    datetime.fromisoformat(
                        str(value).replace("Z", "+00:00")
                    )
                except ValueError:
                    row_errors.append(
                        f"invalid timestamp in field '{field}': {value}"
                    )

        # Optional non-negative integer rule
        for field in integer_fields:
            value = record.get(field)

            if value:
                try:
                    integer_value = int(str(value))

                    if integer_value < 0:
                        row_errors.append(
                            f"negative integer in field '{field}': {value}"
                        )

                except ValueError:
                    row_errors.append(
                        f"invalid integer in field '{field}': {value}"
                    )

        # Duplicate primary key
        if primary_key:
            primary_value = record.get(primary_key)

            if primary_value:
                if primary_value in seen_primary_keys:
                    row_errors.append(
                        f"duplicate {primary_key}: {primary_value}"
                    )
                else:
                    seen_primary_keys.add(primary_value)

        # Duplicate business key
        if business_key:
            business_value = record.get(business_key)

            if business_value:
                if business_value in seen_business_keys:
                    row_errors.append(
                        f"duplicate {business_key}: {business_value}"
                    )
                else:
                    seen_business_keys.add(business_value)

        if row_errors:
            errors.append({
                "row": row_number,
                "errors": row_errors
            })
        else:
            valid_records.append(record)

    return {
        "valid_records": valid_records,
        "errors": errors
    }