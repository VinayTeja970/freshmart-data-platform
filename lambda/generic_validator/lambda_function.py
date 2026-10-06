import boto3
import csv
import io
import json
import urllib.parse

from src.common.s3_utils import parse_s3_key
from src.validation.generic_validator import validate_records

s3 = boto3.client("s3")


def lambda_handler(event, context):
    print("Received event:")
    print(json.dumps(event))

    record = event["Records"][0]

    bucket = record["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        record["s3"]["object"]["key"]
    )

    print(f"Processing: s3://{bucket}/{key}")

    metadata = parse_s3_key(key)

    layer = metadata["layer"]
    dataset = metadata["dataset"]
    load_date = metadata["load_date"]
    filename = metadata["filename"]

    if layer != "raw":
        raise ValueError(
            f"Validator expected raw layer but received: {layer}"
        )

    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    csv_content = response["Body"].read().decode("utf-8")

    reader = csv.DictReader(
        io.StringIO(csv_content)
    )

    records = list(reader)

    print(
        f"Read {len(records)} records "
        f"for dataset '{dataset}'"
    )

    result = validate_records(
        dataset,
        records
    )

    valid_records = result["valid_records"]
    errors = result["errors"]

    print(
        f"Valid records: {len(valid_records)} "
        f"of {len(records)}"
    )

    if errors:
        print("Validation errors:")
        print(json.dumps(errors))

    if not valid_records:
        raise ValueError(
            f"No valid records found for dataset '{dataset}'"
        )

    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=reader.fieldnames
    )

    writer.writeheader()
    writer.writerows(valid_records)

    validated_key = (
        f"validated/{dataset}/"
        f"load_date={load_date}/"
        f"{filename}"
    )

    s3.put_object(
        Bucket=bucket,
        Key=validated_key,
        Body=output.getvalue().encode("utf-8"),
        ContentType="text/csv"
    )

    print(
        f"Validated file written to "
        f"s3://{bucket}/{validated_key}"
    )

    return {
        "statusCode": 200,
        "body": {
            "dataset": dataset,
            "source_key": key,
            "validated_key": validated_key,
            "total_records": len(records),
            "valid_records": len(valid_records),
            "invalid_records": len(errors)
        }
    }