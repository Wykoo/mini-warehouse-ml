#etl extract.py

import os
import pandas as pd
from pathlib import Path

STORAGE = {
    "key": os.getenv("MINIO_ROOT_USER", "admin"),
    "secret": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "client_kwargs": {"endpoint_url": os.getenv("S3_ENDPOINT", "http://localhost:9000")},
}


def upload_local_csv_to_raw(local_path: str, s3_key: str):
    local = Path(local_path)
    if not local.exists():
        raise FileNotFoundError(f"Local file not found: {local}")

    df = pd.read_csv(local)
    s3_uri = f"s3://raw/{s3_key}"
    df.to_csv(s3_uri, index=False, storage_options=STORAGE)
    print(f"Succesfully Uploaded {local} → {s3_uri}  (rows={len(df):,})")

if __name__ == "__main__":
    upload_local_csv_to_raw("data/raw/housing_800k.csv", "housing_800k.csv")