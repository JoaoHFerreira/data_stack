#!/usr/bin/env python3

from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'kaggle_dataset_ingestion',
    default_args=default_args,
    description='Download and process Kaggle datasets',
    schedule_interval=None,
    catchup=False,
    tags=['data-ingestion', 'kaggle'],
)

# Task 1: Create directories with proper permissions
create_dirs_task = BashOperator(
    task_id='create_directories',
    bash_command='mkdir -p /opt/airflow/data/raw/datasets/{{ dag_run.conf.get("dataset_name", "titanic") }} && chmod -R 777 /opt/airflow/data/raw',
    dag=dag,
)

# Task 2: Run Kaggle ingestion
kaggle_ingestion_task = BashOperator(
    task_id='run_kaggle_ingestion',
    bash_command='cd /opt/airflow && PYTHONPATH=/opt/airflow/src python3 /opt/airflow/src/ingestion/kaggle.py {{ dag_run.conf.get("dataset_name", "titanic") }}',
    dag=dag,
)

# Set task dependencies
create_dirs_task >> kaggle_ingestion_task
