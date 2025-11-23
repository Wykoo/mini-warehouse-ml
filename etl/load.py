# etl/load.py
import os
import pandas as pd
from sqlalchemy import create_engine

STORAGE = {
    "key": os.getenv("MINIO_ROOT_USER", "admin"),
    "secret": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "client_kwargs": {"endpoint_url": os.getenv("S3_ENDPOINT", "http://localhost:9000")},
}

PROC_URI = "s3://processed/housing_800k.parquet"

PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
PG_HOST = os.getenv("PG_HOST", "host.docker.internal")  
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB", "warehouse")

PG_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

df = pd.read_parquet(PROC_URI, storage_options=STORAGE)
engine = create_engine(PG_URL)
df.to_sql("housing", engine, schema="public", if_exists="replace", index=False)
print(" Loaded to Postgres public.housing")