import boto3
import copy
import io
import json
import urllib.parse

import pandas as pd

from src.common.s3_utils import parse_s3_key
from src.config.dataset_config import DATASETS

s3 = boto3.client("s3")
glue = boto3.client("glue")

DATABASE_NAME = "freshmart_analytics"


def apply_curated_types(dataset, df):
    config = DATASETS[dataset]

    for field in config.get("string_fields", []):
        if field in df.columns:
            df[field] = df[field].astype("string")

    for field in config.get("timestamp_fields", []):
        if field in df.columns:
            df[field] = pd.to_datetime(
                df[field],
                errors="raise"
            )

    for field in config.get("decimal_fields", []):
        if field in df.columns:
            df[field] = pd.to_numeric(
                df[field],
                errors="raise"
            )
    for field in config.get("integer_fields", []):
        if field in df.columns:
            df[field] = pd.to_numeric(
                df[field],
                errors="raise"
            ).astype("int64")
    for field in config.get("boolean_fields", []):
        if field in df.columns:
            df[field] = (
                df[field]
                .astype(str)
                .str.strip()
                .str.lower()
                .map({
                    "true": True,
                    "false": False,
                    "1": True,
                    "0": False
                })
            )

    return df


def register_partition(
    dataset,
    load_date,
    bucket,
    partition_location
):
    table_name = f"{dataset}_curated"

    table = glue.get_table(
        DatabaseName=DATABASE_NAME,
        Name=table_name
    )

    table_sd = table["Table"]["StorageDescriptor"]

    partition_sd = {
        "Columns": copy.deepcopy(
            table_sd["Columns"]
        ),
        "Location": partition_location,
        "InputFormat": table_sd["InputFormat"],
        "OutputFormat": table_sd["OutputFormat"],
        "SerdeInfo": copy.deepcopy(
            table_sd["SerdeInfo"]
        )
    }

    partition_input = {
        "Values": [load_date],
        "StorageDescriptor": partition_sd
    }

    try:
        glue.create_partition(
            DatabaseName=DATABASE_NAME,
            TableName=table_name,
            PartitionInput=partition_input
        )

        print(
            f"Registered Glue partition "
            f"{table_name}: load_date={load_date}"
        )

        return "created"

    except glue.exceptions.AlreadyExistsException:
        glue.update_partition(
            DatabaseName=DATABASE_NAME,
            TableName=table_name,
            PartitionValueList=[load_date],
            PartitionInput=partition_input
        )

        print(
            f"Updated existing Glue partition "
            f"{table_name}: load_date={load_date}"
        )

        return "updated"


def lambda_handler(event, context):
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

    if layer != "validated":
        raise ValueError(
            f"Curator expected validated layer "
            f"but received: {layer}"
        )

    if dataset not in DATASETS:
        raise ValueError(
            f"Unsupported dataset: {dataset}"
        )

    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    csv_bytes = response["Body"].read()

    df = pd.read_csv(
        io.BytesIO(csv_bytes),
        dtype=str
    )

    print(
        f"Read {len(df)} records "
        f"for dataset '{dataset}'"
    )

    if df.empty:
        raise ValueError(
            f"Validated file is empty: {key}"
        )

    df = apply_curated_types(
        dataset,
        df
    )

    curated_key = (
        f"curated/{dataset}/"
        f"load_date={load_date}/"
        f"{dataset}.parquet"
    )

    output = io.BytesIO()

    df.to_parquet(
        output,
        engine="pyarrow",
        compression="snappy",
        index=False
    )

    output.seek(0)

    s3.put_object(
        Bucket=bucket,
        Key=curated_key,
        Body=output.getvalue(),
        ContentType="application/octet-stream"
    )

    print(
        f"Parquet written to "
        f"s3://{bucket}/{curated_key}"
    )

    partition_location = (
        f"s3://{bucket}/curated/{dataset}/"
        f"load_date={load_date}/"
    )

    partition_action = register_partition(
        dataset=dataset,
        load_date=load_date,
        bucket=bucket,
        partition_location=partition_location
    )

    return {
        "statusCode": 200,
        "body": {
            "dataset": dataset,
            "source_key": key,
            "curated_key": curated_key,
            "records": len(df),
            "partition_action": partition_action
        }
    }