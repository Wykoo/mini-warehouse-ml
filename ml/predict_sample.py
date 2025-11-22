# ml/predict_new.py
import os
from pathlib import Path
from datetime import datetime, timezone

import joblib
import pandas as pd
from sqlalchemy import create_engine

# --- Stałe ---
ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True, parents=True)

MODEL_PATH = next(ARTIFACTS_DIR.glob("best_model_*.joblib"))

TARGET_COL = "price_total"
SOURCE_TABLE = "gold.housing_valid"  
PRED_SCHEMA = "gold"
PRED_TABLE = "housing_predictions"    

PG_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('PG_USER', 'postgres')}:"
    f"{os.getenv('PG_PASSWORD', 'postgres')}@"
    f"{os.getenv('PG_HOST', 'localhost')}:"
    f"{os.getenv('PG_PORT', '5432')}/"
    f"{os.getenv('PG_DB', 'warehouse')}"
)


def load_model():
    print(f"Ładowanie modelu z: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    return model


def load_new_flats(engine, n: int = 10) -> pd.DataFrame:
    """
    Na start: weź 10 losowych mieszkań z gold.housing_valid.
    """
    query = f"""
        SELECT *
        FROM {SOURCE_TABLE}
        ORDER BY random()
        LIMIT {n}
    """
    df = pd.read_sql(query, engine)
    return df


def main():
    engine = create_engine(PG_URL)
    model = load_model()

    print("Pobieranie mieszkań do wyceny...")
    df = load_new_flats(engine, n=10)

    if "listing_id" not in df.columns:
        raise ValueError("Brakuje kolumny 'listing_id' w gold.housing_valid")
    id_cols = ["listing_id"]

    feature_df = df.drop(columns=[c for c in [TARGET_COL] if c in df.columns])

    print("Liczenie predykcji...")
    y_pred = model.predict(feature_df)

    now = datetime.now(timezone.utc)

    pred_df = pd.DataFrame({
        "listing_id": df["listing_id"],
        "predicted_price_total": y_pred,
        "scored_at": now,
        "model_path": str(MODEL_PATH.name),
    })

    print("Zapisywanie predykcji do bazy...")
    pred_df.to_sql(
        PRED_TABLE,
        engine,
        schema=PRED_SCHEMA,
        if_exists="append",
        index=False,
    )
    print(f"Zapisano {len(pred_df)} predykcji {PRED_SCHEMA}.{PRED_TABLE}")

    
    report_df = df.merge(pred_df, on="listing_id", how="inner")

    if TARGET_COL in report_df.columns:
        report_df["diff"] = report_df["predicted_price_total"] - report_df[TARGET_COL]
        report_df["diff_pct"] = (
            report_df["diff"] / report_df[TARGET_COL].replace(0, pd.NA) * 100
        ).round(2)

    report_excel = report_df.copy()
    if "scored_at" in report_excel.columns:
        if pd.api.types.is_datetime64tz_dtype(report_excel["scored_at"]):
            report_excel["scored_at"] = report_excel["scored_at"].dt.tz_localize(None)
    
    if "listing_date" in report_excel.columns:
        report_excel["listing_date"] = pd.to_datetime(report_excel["listing_date"]).dt.date


    excel_name = f"predictions_{now.strftime('%Y%m%d_%H%M')}.xlsx"
    excel_path = ARTIFACTS_DIR / excel_name
    report_excel.to_excel(excel_path, index=False)
    print(f"Zapisano raport do Excela → {excel_path}")

    print("Podgląd 5 wierszy:")
    print(report_excel.head())


if __name__ == "__main__":
    main()