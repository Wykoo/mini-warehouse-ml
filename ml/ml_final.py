import os
from pathlib import Path

import joblib
import pandas as pd
import numpy as np
import time
import hashlib
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
from xgboost import XGBRegressor


# 1.Konfiguracja

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True, parents=True)

TARGET_COL = "price_total"          
TABLE_NAME = "gold.housing_valid"   

PG_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('PG_USER', 'postgres')}:"
    f"{os.getenv('PG_PASSWORD', 'postgres')}@"
    f"{os.getenv('PG_HOST', 'localhost')}:"
    f"{os.getenv('PG_PORT', '5432')}/"
    f"{os.getenv('PG_DB', 'warehouse')}"
)

def hash256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest() 

def load_data() -> pd.DataFrame:
    engine = create_engine(PG_URL)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", engine)
    df = df.sample(frac= 0.05, random_state=42) 
    return df

def build_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    num_cols = df.select_dtypes(include=["float64", "int64"]).columns.to_list()
    num_cols = [c for c in num_cols if c != TARGET_COL]

    cat_cols = df.select_dtypes(exclude=["float64", "int64"]).columns.to_list()

    num_transformer = Pipeline(steps=[
        ("Imputer", SimpleImputer(strategy='median')),
        ("scaler", StandardScaler())
    ])

    cat_transfomer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy='most_frequent')),
        ("encoder", OneHotEncoder(handle_unknown='ignore'))
    ])

    pre_processor = ColumnTransformer(transformers=[
        ("num", num_transformer, num_cols),
        ("cat", cat_transfomer, cat_cols)
    ])

    return pre_processor, num_cols, cat_cols

def get_models():
    models = {
        "RandomForest": RandomForestRegressor(
        n_estimators=50,
        max_depth=12,
        n_jobs=-1,
        random_state=42
    ),
        "GradientBoosting": GradientBoostingRegressor(
        learning_rate=0.05,
        n_estimators=50,
        max_depth=3,
        random_state=42
    ),
        "XGBRegressor": XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss",
        n_jobs=-1
    )  
    }
    return models

def param_grids():
    param_grids = {
        "RandomForest": {
            "model__n_estimators": [50, 100, 150],
            "model__max_depth": [5, 10, 15, None],
            "model__min_samples_split": [2, 5, 10]
        },

        "GradientBoosting": {
            "model__n_estimators": [50, 100, 150],
            "model__learning_rate": [0.03, 0.05, 0.1],
            "model__max_depth": [2, 3, 4]
        },

        "XGBRegressor": {
            "model__n_estimators": [100, 150, 200],
            "model__learning_rate": [0.03, 0.05, 0.1],
            "model__max_depth": [3, 4, 5],
            "model__subsample": [0.7, 0.8, 0.9],
            "model__colsample_bytree": [0.7, 0.8, 0.9]
        }
    }

    return param_grids

def train_and_evaluate():
    df = load_data()
    y = df[TARGET_COL]
    X = df.drop(columns=[TARGET_COL])
    pre_processor, num_cols, cat_cols = build_preprocessor(df)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    X_test, X_valid, y_test, y_valid = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )

    models = get_models()
    grids = param_grids()
    results = []

    best_model_name = None
    best_pipeline = None
    best_mae = np.inf
    best_rmse = None
    best_r2 = None

    for name, model in models.items():
        print(f"\n=== Trenowany model: {name} ===")

        pipe = Pipeline([
            ("pre", pre_processor),
            ("model", model)
        ])

        search = RandomizedSearchCV(
            estimator=pipe,
            param_distributions=grids[name],
            n_iter=5,
            scoring="neg_mean_absolute_error",
            cv=2,
            n_jobs=1,
            verbose=1,
            random_state=42
        )

        start = time.time()

        try:
            search.fit(X_train, y_train)
            best_pipe = search.best_estimator_
            best_params = search.best_params_
        except Exception as e:
            print(f"[ERROR] RandomizedSearchCV failed for {name}: {e}")
            best_pipe = pipe.fit(X_train, y_train)
            best_params = None

        end = time.time()

        y_pred_valid = best_pipe.predict(X_valid)

        mae  = mean_absolute_error(y_valid, y_pred_valid)
        rmse = root_mean_squared_error(y_valid, y_pred_valid)
        r2   = r2_score(y_valid, y_pred_valid)

        results.append({
            "model": name,
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "best_params": best_params
        })

        print(f"MAE  = {mae:,.2f}")
        print(f"RMSE = {rmse:,.2f}")
        print(f"R²   = {r2:,.4f}")
        print(f"Czas trenowania: {end - start:.2f}s")

        if mae < best_mae:
            best_mae = mae
            best_model_name = name
            best_pipeline = best_pipe
            best_r2 = r2
            best_rmse = rmse

    results_df = pd.DataFrame(results).sort_values("mae")
    results_path = ARTIFACTS_DIR / "model_metrics.csv"
    results_df.to_csv(results_path, index=False)
    print(f"\nZapisano metryki: {results_path}")

    best_model_path = ARTIFACTS_DIR / f"best_model_{best_model_name}.joblib"
    joblib.dump(best_pipeline, best_model_path)
    print(f"Najlepszy model: {best_model_name} (MAE={best_mae:,.2f})")
    print(f"Zapisano pipeline do: {best_model_path}")

    pipeline_sha = hash256(best_model_path)
    print(f"SHA256 pipeline’u: {pipeline_sha}")

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    scored_at = datetime.now(timezone.utc)
    train_rows = len(X_train)
    valid_rows = len(X_valid)

    run_row = pd.DataFrame([{
        "run_id": run_id,
        "model_name": best_model_name,
        "mae": best_mae,
        "rmse": best_rmse,
        "r2": best_r2,
        "train_rows": train_rows,
        "valid_rows": valid_rows,
        "scored_at": scored_at,
        "pipeline_sha": pipeline_sha,
    }])

    engine = create_engine(PG_URL)
    run_row.to_sql(
        "model_runs",
        engine,
        schema="ml",
        if_exists="append",
        index=False
    )
    print("Zapisano metadane runu do ml.model_runs")

if __name__ == "__main__":
    train_and_evaluate()