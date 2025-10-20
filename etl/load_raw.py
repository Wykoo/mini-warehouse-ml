# etl/load_raw.py
import os
import argparse
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

STORAGE = {
    "key": os.getenv("MINIO_ROOT_USER", "admin"),
    "secret": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "client_kwargs": {"endpoint_url": os.getenv("S3_ENDPOINT", "http://localhost:9000")},
}

PG_URL = (
    f"postgresql+psycopg2://{os.getenv('PG_USER','postgres')}:"
    f"{os.getenv('PG_PASSWORD','postgres')}@"
    f"{os.getenv('PG_HOST','localhost')}:{os.getenv('PG_PORT','5432')}/"
    f"{os.getenv('PG_DB','postgres')}"
)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="ścieżka do pliku w MinIO, np. s3://raw/housing.csv")
    ap.add_argument("--table", default="housing_raw", help="tabela docelowa w Postgresie")
    args = ap.parse_args()

    # Wczytaj CSV / Parquet z MinIO
    if args.src.endswith(".parquet"):
        df = pd.read_parquet(args.src, storage_options=STORAGE)
    else:
        df = pd.read_csv(args.src, storage_options=STORAGE)

    engine = create_engine(PG_URL)
    df.to_sql(args.table, engine, schema="public", if_exists="replace", index=False)

    print(f"Surowe dane załadowane do tabeli {args.table} ({len(df):,} wierszy)")

if __name__ == "__main__":
    main()