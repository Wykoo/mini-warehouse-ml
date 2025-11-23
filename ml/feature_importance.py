import joblib
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


ARTIFACTS_DIR = Path("artifacts")
MODEL_PATH = next(ARTIFACTS_DIR.glob("best_model_*.joblib"), None)
OUTPUT_CSV = ARTIFACTS_DIR / "feature_importance.csv"
OUTPUT_PNG = ARTIFACTS_DIR / "feature_importance.png"


def main():
    if MODEL_PATH is None:
        raise FileNotFoundError("Nie znaleziono pliku best_model_*.joblib w artifacts/")

    print(f"Ładowanie modelu: {MODEL_PATH} ...")
    model = joblib.load(MODEL_PATH)

    pre = model.named_steps["pre"]
    model_step = model.named_steps["model"]

    if not hasattr(model_step, "feature_importances_"):
        raise ValueError("Ten model nie wspiera feature_importances_")

    print("Generowanie listy cech...")
    feature_names = pre.get_feature_names_out()

    print("Pobieranie wartości feature_importances_...")
    importances = model_step.feature_importances_

    df = pd.DataFrame(
        {"feature": feature_names, "importance": importances}
    ).sort_values("importance", ascending=False)
    df_top = df.head(20).reset_index(drop=True)

    df_top.to_csv(OUTPUT_CSV, index=False)
    print(f"Zapisano CSV → {OUTPUT_CSV}")

    plt.figure(figsize=(8, 10))
    plt.barh(df_top["feature"], df_top["importance"])
    plt.gca().invert_yaxis()
    plt.title("Feature Importance - TOP 20")
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG)
    plt.close()

    print(f"Zapisano wykres → {OUTPUT_PNG}")
    print("DONE ✔")


if __name__ == "__main__":
    main()