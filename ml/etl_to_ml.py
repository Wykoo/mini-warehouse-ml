# etl_to_ml.py
import pandas as pd
from sqlalchemy import create_engine
import os

DB_URL = os.getenv(
    "DB_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/warehouse"
)

def load_housing_valid() -> pd.DataFrame:
    engine = create_engine(DB_URL)
    return pd.read_sql("SELECT * FROM gold.housing_valid;", engine)

if __name__ == "__main__":
    df = load_housing_valid()
    print(df.head())
    print(f"\nZaładowano {len(df)} rekordów ✅")
    