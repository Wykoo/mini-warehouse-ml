# etl/transform.py
import os
import argparse
from typing import List, Tuple

import pandas as pd
import numpy as np


STORAGE = {
    "key": os.getenv("MINIO_ROOT_USER", "admin"),
    "secret": os.getenv("MINIO_ROOT_PASSWORD", "admin12345"),
    "client_kwargs": {"endpoint_url": os.getenv("S3_ENDPOINT", "http://localhost:9000")},
}

RAW_BUCKET = os.getenv("RAW_BUCKET", "raw")
PROC_BUCKET = os.getenv("PROC_BUCKET", "processed")


# ---------------------------------------------------------------------
# 1) Read raw data
# ---------------------------------------------------------------------
def read_raw_csv(key: str) -> pd.DataFrame:
    """Read raw CSV file from S3/MinIO."""
    src_uri = f"s3://{RAW_BUCKET}/{key}"
    df = pd.read_csv(src_uri, storage_options=STORAGE)
    return df


# ---------------------------------------------------------------------
# 2) Type parsing
# ---------------------------------------------------------------------
def parse_dates(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Convert string date column into datetime type."""
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    return df


# ---------------------------------------------------------------------
# 3) Missing values imputation
# ---------------------------------------------------------------------
def impute_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Fill NaN values in numeric columns with the median."""
    num_cols = df.select_dtypes(include=["float64", "int64"]).columns
    for c in num_cols:
        if df[c].isna().any():
            df[c] = df[c].fillna(df[c].median())
    return df


def impute_binary(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """Fill NaN values in binary columns with 1 (assume 'yes') and cast to int."""
    for c in cols:
        if c in df.columns and df[c].isna().any():
            df[c] = df[c].fillna(1).astype(int)
    return df


# ---------------------------------------------------------------------
# 4) Feature engineering
# ---------------------------------------------------------------------
def add_age_years(
    df: pd.DataFrame, date_col: str = "date", built_col: str = "year_built"
) -> pd.DataFrame:
    """Add 'age_years' = difference between transaction year and year built (clipped at 0)."""
    if date_col in df.columns and built_col in df.columns:
        df["age_years"] = (df[date_col].dt.year - df[built_col]).clip(lower=0)
    return df


def add_floor_ratio(
    df: pd.DataFrame, floor: str = "floor", total: str = "total_floors"
) -> pd.DataFrame:
    """Add 'floor_ratio' = floor / total_floors (clipped between 0 and 1)."""
    if {floor, total}.issubset(df.columns):
        with np.errstate(divide="ignore", invalid="ignore"):
            df["floor_ratio"] = (df[floor] / df[total]).clip(0, 1)
            df["floor_ratio"] = df["floor_ratio"].fillna(0)
    return df


def add_date_parts(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Extract year, month, day, and day-of-week from the date column."""
    if date_col in df.columns:
        df["year"] = df[date_col].dt.year
        df["month"] = df[date_col].dt.month
        df["day"] = df[date_col].dt.day
        df["dow"] = df[date_col].dt.dayofweek
    return df


# ---------------------------------------------------------------------
# 5) Write processed data
# ---------------------------------------------------------------------
def write_processed_parquet(df: pd.DataFrame, key: str) -> str:
    """Save processed DataFrame to S3/MinIO as parquet file."""
    dst_uri = f"s3://{PROC_BUCKET}/{key}"
    df.to_parquet(dst_uri, index=False, storage_options=STORAGE)
    return dst_uri


# ---------------------------------------------------------------------
# 6) Full transformation pipeline
# ---------------------------------------------------------------------
def transform_pipeline(src_key: str, dst_key: str) -> Tuple[pd.DataFrame, str]:
    """Full ETL pipeline: read → clean → feature engineering → write."""
    df = read_raw_csv(src_key)

    # Apply all transformations step by step
    df = parse_dates(df, "date")
    df = impute_numeric(df)
    df = impute_binary(df, cols=["has_elevator"])
    df = add_age_years(df, "date", "year_built")
    df = add_floor_ratio(df, "floor", "total_floors")
    df = add_date_parts(df, "date")

    uri = write_processed_parquet(df, dst_key)
    return df, uri


# ---------------------------------------------------------------------
# 7) Command-line interface
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Transform raw housing CSV into processed parquet."
    )
    parser.add_argument(
        "--src",
        required=True,
        help="Filename in bucket 'raw', e.g. housing_800k.csv",
    )
    parser.add_argument(
        "--dst",
        required=True,
        help="Filename in bucket 'processed', e.g. housing_800k.parquet",
    )
    args = parser.parse_args()

    df, uri = transform_pipeline(args.src, args.dst)
    print(f" Processed {len(df):,} rows → {uri}")


if __name__ == "__main__":
    main()