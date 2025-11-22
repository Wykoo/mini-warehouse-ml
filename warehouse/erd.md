# 🏗️ Mini Warehouse ML – Data Warehouse & ML Pipeline

Poniższy dokument przedstawia pełną architekturę hurtowni danych oraz pipeline ML projektu **Mini Warehouse ML**.

Obejmuje warstwy:

**bronze → silver → gold → ml**

wraz z przepływem danych, walidacją, trenowaniem modeli i generowaniem predykcji.

---

# 📊 ERD – Zależności między tabelami (Mermaid)

```mermaid
flowchart TD

    %% --- BRONZE ---
    subgraph BRONZE ["Bronze Layer – Raw Data"]
        B1["bronze.raw_listings"]
        B2["bronze.raw_agents"]
        B3["bronze.raw_locations"]
    end

    %% --- SILVER ---
    subgraph SILVER ["Silver Layer – Cleaned & Standardized"]
        S1["silver.listings_clean"]
        S2["silver.agents_clean"]
        S3["silver.locations_clean"]
        S4["silver.listings_enriched"]
    end

    %% --- GOLD ---
    subgraph GOLD ["Gold Layer – Analytics-Ready"]
        G1["gold.housing_base"]
        G2["gold.housing_features"]
        G3["gold.housing_valid"]
    end

    %% --- ML ---
    subgraph ML ["ML Layer – Predictions & Metadata"]
        M1["ml.housing_predictions"]
        M2["ml.model_runs"]
    end

    %% ---------------- FLOWS ----------------

    %% Bronze → Silver
    B1 --> S1
    B2 --> S2
    B3 --> S3

    %% Enrichment
    S1 --> S4
    S3 --> S4

    %% Silver → Gold
    S4 --> G1
    G1 --> G2
    G2 --> G3

    %% Gold → ML
    G3 -->|"predict_sample.py"| M1

    %% Model metadata
    M2 <--|"ml_final.py (training logs)"| G3

    %% Relationships
    S2 -.-> S4
    B2 -.-> S2
```

## 📦 Warstwy hurtowni danych

### 🔹 Bronze — Raw Layer

Zawiera dane w formie najbardziej zbliżonej do źródła.
• bronze.raw_listings
• bronze.raw_agents
• bronze.raw_locations

✔ brak walidacji
✔ brak typowania
✔ struktura “as-is”

### 🔸 Silver — Clean Layer

Dane po transformacji:
• usunięte wartości błędne
• poprawione typy
• normalizacja kolumn
• łączenie danych z kilku źródeł (listings_enriched)

### 🟡 Gold — Feature Layer

Warstwa używana do analiz i ML:
• housing_base — agregacje i dane końcowe
• housing_features — wszystkie cechy numeryczne & kategoryczne
• housing_valid — ostateczny zbiór treningowy / walidacyjny

### 🟢 ML — Model Predictions & Metadata

ml.housing_predictions
Zawiera predykcje wygenerowane przez model:
• listing_id
• predicted_price_total
• scored_at
• model_path
• diff_real_vs_pred (opcjonalnie)

Tworzone przez skrypt:

```bash
python ml/predict_sample.py
```

**gold.model_runs**
Log każdego treningu:
• run_id
• model_name
• mae, rmse, r2
• train_rows, valid_rows
• scored_at
• pipeline_sha (hash pliku modelu)

Tworzone przez skrypt:

```bash
python ml/ml_final.py
```

### 🚀 Pipeline ML – skrót działania

    1.	Feature engineering (gold_features w Airflow)
    2.	Walidacja (gold_valid)
    3.	Trenowanie modeli (RandomForest, GradientBoosting, XGBoost)
    4.	Wybór najlepszego modelu (najniższe MAE)
    5.	Zapis pipeline’u do artifacts/
    6.	Obliczenie SHA256 pipeline’u
    7.	Zapis wyników do ml.model_runs
    8.	Generowanie predykcji na nowych danych
    9.	Zapis predykcji do DB + Excel

### 📂 Struktura katalogów projektu

```bash
mini-warehouse-ml/
│
├── airflow/                # DAG ETL + ML
├── artifacts/              # zapisany pipeline + modele + wykresy
├── data/                   # pliki wejściowe (opcjonalnie)
├── etl/                    # transformacje SQL / Python
├── ml/                     # model ML + SHAP + predykcje
├── notebooks/              # exploratory work & drafts
├── SQL/                    # pełny zestaw DDL/DML do hurtowni
└── requirements.txt        # zależności projektu
```
