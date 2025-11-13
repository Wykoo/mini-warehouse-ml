# 🏗️ Mini Warehouse ML – End-to-End Data Engineering Pipeline

Kompleksowy projekt Data Engineering z pełnym pipeline'em ETL działającym w stylu produkcyjnym:

- Apache Airflow — orkiestracja
- MinIO (S3) — storage plików
- PostgreSQL — baza danych bronze/silver/gold
- Python + Pandas — transformacje
- SQL — walidacja, czyszczenie i feature engineering
- Docker Compose — pełna infrastruktura lokalna

Całość jest zaprojektowana jako portfolio-quality project.

---

# 📂 Architektura

  Raw CSV → Bronze (Pandas → Parquet → MinIO)
                     ↓
  Silver (SQL: typing, cleaning, validation)
                     ↓
  Gold (Feature engineering, KPI views, modeling)

  DAG Airflow (`warehouse_daily`) kontroluje wszystkie kroki.

---

# 📁 Struktura repozytorium

```
mini-warehouse-ml/
│
├── airflow/
│   ├── dags/
│   │   └── warehouse_dag.py
│   ├── repo/
│   │   ├── etl/
│   │   │   ├── extract.py
│   │   │   ├── transform.py
│   │   │   └── load.py
│   │   └── SQL/
│   │       ├── SQL_raw/
│   │       │   └── 01_staging/
│   │       ├── SQL_silver/
│   │       └── SQL_gold/
│   ├── .env.example
│   └── docker-compose.airflow.yml
│
├── data/
│   └── housing_800k.csv
│
└── README.md
```

---

# ⚙️ Instalacja i uruchomienie

Poniżej instrukcja 1:1, aby każdy mógł powtórzyć projekt.

---

## 1️⃣ Utwórz plik `.env`

W katalogu `airflow/`:

```bash
cp airflow/.env.example airflow/.env
```

Edytuj:
```bash
nano airflow/.env
```

## 2️⃣ Uzupełnij .env swoimi wartościami

# === SECURITY ===
AIRFLOW__CORE__FERNET_KEY=<WSTAW_TUTAJ_FERNET_KEY>
AIRFLOW__WEBSERVER__SECRET_KEY=<WSTAW_TUTAJ_SECRET_KEY>

# === AIRFLOW ADMIN ===
_AIRFLOW_WWW_USER_CREATE=True
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin123

# === POSTGRES CONNECTION FOR DAG ===
PG_HOST=host.docker.internal
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=postgres
PG_DB=warehouse

# === MINIO ===
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=admin12345
S3_ENDPOINT=http://host.docker.internal:9000

## 3️⃣ Wygeneruj klucze

Fernet Key:
```bash
python3 - <<'EOF'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
```

Secret Key:
```bash
openssl rand -hex 64
```

Wklej oba do .env.

## 4️⃣ Uruchom środowisko

```bash
docker compose -f docker-compose.airflow.yml up -d
```

Airflow UI:
👉 http://localhost:8081

Login:
```bash
Username: admin
Password: admin123
```

## ▶️ Uruchamianie DAG-a

W Airflow aktywuj DAG:

**warehouse_daily**

Pipeline wykona kolejno:
	1.	Extract → upload CSV to MinIO
	2.	Transform → Parquet
	3.	Load → Postgres bronze
	4.	Silver typing & missing value handling
	5.	Silver logic checks
	6.	Gold feature engineering
	7.	Gold validation views

## 🗄️ Warstwy bazy danych

**Bronze**
	•	bronze.housing_raw

**Silver**
	•	silver.housing_typed
	•	silver.housing_clean

**Gold**
	•	gold.housing_features
	•	gold.kpi_overview
	•	gold.housing_valid
	•	gold.housing_invalid
	•	gold.duplicates

## 🧠 Feature Engineering (Gold)

Cechy wyliczane:
	•	floor_ratio
	•	decade
	•	season
	•	building_age
	•	area_sqm_bucket
	•	distance_km_bucket
	•	listing_day_of_week
	•	has_elevator_int


Kod SQL znajduje się w:
```bash
airflow/repo/SQL/SQL_gold/
```

## 🔄 Restart środowiska

Stop:
```bash
docker compose -f docker-compose.airflow.yml down
```

Start:
```bash
docker compose -f docker-compose.airflow.yml up -d
```
