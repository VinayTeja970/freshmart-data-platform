from pathlib import Path

import boto3


BUCKET_NAME = "freshmart-data-2026"


def upload_file_to_s3(local_file, s3_key):
    local_file = Path(local_file)

    if not local_file.exists():
        raise FileNotFoundError(
            f"Local file does not exist: {local_file}"
        )

    s3 = boto3.client("s3")

    print(f"Uploading {local_file}...")
    print(f"Destination: s3://{BUCKET_NAME}/{s3_key}")

    s3.upload_file(
        str(local_file),
        BUCKET_NAME,
        s3_key
    )

    print("Upload completed successfully")
