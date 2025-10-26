from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import os
from pathlib import Path

DAG_ID = "sales_pipeline"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def run_ingest(**context):
    # runs the ingestion script inside mounted volume
    script = "/opt/ingest/ingest_to_postgres.py"
    os.system(f"python3 {script}")


with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="ELT pipeline: MinIO -> Postgres -> dbt -> Streamlit",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    t1_download = PythonOperator(
        task_id="ingest_from_minio",
        python_callable=run_ingest,
    )

    t2_dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/dbt && dbt deps && dbt run --profiles-dir .",
    )

    t3_dbt_test = BashOperator(
        task_id="dbt_test", bash_command="cd /opt/dbt && dbt test --profiles-dir ."
    )

    t1_download >> t2_dbt_run >> t3_dbt_test
