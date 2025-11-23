from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.common.sql.sensors.sql import SqlSensor 

REPO = "/opt/airflow/repo"

default_args = {
    "owner": "wyko",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="warehouse_daily",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 6 * * *",      
    catchup=False,
    template_searchpath=[f"{REPO}/SQL"], 
    default_args=default_args,
    tags=["warehouse","bronze-silver-gold"],
) as dag:

    wait_db = SqlSensor(
        task_id="wait_for_db",
        conn_id="warehouse_pg",
        poke_interval=15,
        timeout=600,
        mode="reschedule",
        sql="SELECT 1;"
    )

    extract_to_minio = BashOperator(
        task_id="extract_to_minio",
        bash_command="cd /opt/airflow/repo && python etl/extract.py"
    )

    transform_to_parquet = BashOperator(
        task_id="transform_to_parquet",
        bash_command=(
            f"python {REPO}/etl/transform.py "
            f"--src housing_800k.csv "
            f"--dst housing_800k.parquet"
        )
    )

    load_processed_to_pg = BashOperator(
        task_id="load_processed_to_pg",
        bash_command=f"python {REPO}/etl/load.py"
    )

    silver_handle_missing = SQLExecuteQueryOperator(
        task_id="silver_handle_missing",
        conn_id="warehouse_pg",
        sql="SQL_raw/01_staging/110_handle_missing_values.sql",
    )
    silver_cast_normalize = SQLExecuteQueryOperator(
        task_id="silver_cast_normalize",
        conn_id="warehouse_pg",
        sql="SQL_raw/01_staging/120_cast_and_normalize.sql",
    )
    silver_logic_checks = SQLExecuteQueryOperator(
        task_id="silver_logic_checks",
        conn_id="warehouse_pg",
        sql="SQL_raw/01_staging/130_handle_logic.sql",
    )

    gold_features = SQLExecuteQueryOperator(
        task_id="gold_features",
        conn_id="warehouse_pg",
        sql="SQL_raw/02_gold/210_gold_features.sql",
    )
    gold_valid = SQLExecuteQueryOperator(
        task_id="gold_valid",
        conn_id="warehouse_pg",
        sql="SQL_raw/02_gold/220_gold_valid.sql",
    )
    train_models = BashOperator(
        task_id="train_models",
        bash_command=f"cd {REPO} && python ml/ml_final.py",
    )
    feature_importance = BashOperator(
        task_id="feature_importance_ml",
        bash_command=f"cd {REPO} && python ml/feature_importance.py"
    )
    shap_explainer = BashOperator(
        task_id="shap_explainer_ml",
        bash_command=f"cd {REPO} && python ml/shap_explainer.py"
    )
    Model_prediction = BashOperator(
        task_id="Model_prediction_sample",
        bash_command=f"cd {REPO} && python ml/predict_sample.py"
    )
    # Pipeline
    wait_db >> extract_to_minio >> transform_to_parquet >> load_processed_to_pg
    load_processed_to_pg >> [silver_handle_missing, silver_cast_normalize] >> silver_logic_checks
    silver_logic_checks >> gold_features >> gold_valid >> train_models >> feature_importance >> shap_explainer 
    shap_explainer >> Model_prediction