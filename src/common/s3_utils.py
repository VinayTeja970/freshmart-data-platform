from datetime import datetime
from src.config.dataset_config import DATASETS

def parse_s3_key(s3_key):
    """
    Parse a FreshMart S3 object key.

    Expected structure:
        <layer>/<dataset>/load_date=YYYY-MM-DD/<file>

    Example:
        raw/customers/load_date=2026-10-08/customers.csv

    Returns:
        {
            "layer": "raw",
            "dataset": "customers",
            "load_date": "2026-10-08",
            "filename": "customers.csv"
        }
    """

    parts = s3_key.split("/")

    if len(parts) != 4:
        raise ValueError(
            f"Invalid FreshMart S3 key structure: {s3_key}"
        )

    layer = parts[0]
    dataset = parts[1]
    partition = parts[2]
    filename = parts[3]

    valid_layers = {
        "raw",
        "validated",
        "curated"
    }

    if layer not in valid_layers:
        raise ValueError(
            f"Invalid FreshMart layer '{layer}' in key: {s3_key}"
        )

    if not dataset:
        raise ValueError(
            f"Dataset is missing from key: {s3_key}"
        )
    if dataset not in DATASETS:
        raise ValueError(
            f"Unsupported dataset '{dataset}' in key: {s3_key}"
        )
    if not partition.startswith("load_date="):
        raise ValueError(
            f"Missing load_date partition in key: {s3_key}"
        )

    load_date = partition.split("=", 1)[1]

    try:
        datetime.strptime(load_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"Invalid load_date '{load_date}' in key: {s3_key}"
        )

    if not filename:
        raise ValueError(
            f"Filename is missing from key: {s3_key}"
        )

    return {
        "layer": layer,
        "dataset": dataset,
        "load_date": load_date,
        "filename": filename
    }


def extract_dataset_from_key(s3_key):
    return parse_s3_key(s3_key)["dataset"]