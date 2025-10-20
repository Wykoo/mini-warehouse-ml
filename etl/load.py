import os
import pandas as pd
from sqlalchemy import create_engine

STORAGE = {
    "key": os.getenv("MINIO_ROOT_USER", "admin"),
    "secret": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "client_kwargs": {"endpoint_url": os.getenv("S3_ENDPOINT", "http://localhost:9000")},
}

PROC_URI = "s3://processed/housing_800k.parquet"
PG_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"

df = pd.read_parquet(PROC_URI, storage_options=STORAGE)
engine = create_engine(PG_URL)
df.to_sql("housing", engine, schema="public", if_exists="replace", index=False)
print(" Loaded to Postgres public.housing")