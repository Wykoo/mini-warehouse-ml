import pandas as pd
import joblib
import numpy as np
if not hasattr(np, "bool"):
    np.bool = bool
import shap
import matplotlib.pyplot as plt
from pathlib import Path
from sqlalchemy import create_engine
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODEL_PATH = next(ARTIFACTS_DIR.glob("best_model_*.joblib"))
OUTPUT_PNG = ARTIFACTS_DIR / "shap_summary.png"
OUTPUT_CSV = ARTIFACTS_DIR / "shap_values.csv"

PG_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('PG_USER', 'postgres')}:"
    f"{os.getenv('PG_PASSWORD', 'postgres')}@"
    f"{os.getenv('PG_HOST', 'localhost')}:"
    f"{os.getenv('PG_PORT', '5432')}/"
    f"{os.getenv('PG_DB', 'warehouse')}"
)

TARGET_COL = "price_total"
TABLE_NAME = "gold.housing_valid"

def load_sample():
    """Pobiera próbkę 2% do SHAP (żeby nie zabić pamięci)"""
    engine = create_engine(PG_URL)
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", engine)
    return df.sample(5000, random_state=42)

def main():
    print(f"Ładowanie modelu: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)

    pre = model.named_steps["pre"]
    model_step = model.named_steps["model"]

    print("Pobieranie próby danych...")
    df = load_sample()
    X = df.drop(columns=[TARGET_COL])

    print("Transformacja danych...")
    X_pre = pre.transform(X)

    if hasattr(X_pre, "toarray"):
        X_pre = X_pre.toarray()

    X_pre = X_pre.astype("float64")

    print("Obliczanie wartości SHAP...")
    explainer = shap.TreeExplainer(model_step)
    shap_values = explainer.shap_values(X_pre)

    print("Zapis do CSV...")
    pd.DataFrame(shap_values).to_csv(OUTPUT_CSV, index=False)
    print(f"Zapisano SHAP CSV → {OUTPUT_CSV}")

    print("Rysowanie wykresu (bar plot)...")

    try:
        feature_names = pre.get_feature_names_out()
    except Exception:
        feature_names = None

    plt.figure(figsize=(10, 8))
    shap.summary_plot(
        shap_values,
        X_pre,
        feature_names=feature_names,
        show=False,
        plot_type="bar",    
        max_display=20      
    )

    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, bbox_inches="tight")
    plt.close()

    print(f"Wykres zapisany → {OUTPUT_PNG}")
    print("DONE ✔")

if __name__ == "__main__":
    main()

    