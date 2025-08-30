#!/usr/bin/env python3

from datetime import timedelta
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

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
    'kaggle_k8s_ingestion',
    default_args=default_args,
    description='Download Kaggle datasets using KubernetesPodOperator',
    schedule_interval=None,
    catchup=False,
    tags=['data-ingestion', 'kaggle', 'kubernetes'],
)

# Kubernetes Pod Operator for Kaggle processing
kaggle_k8s_task = KubernetesPodOperator(
    task_id='kaggle_processor_pod',
    name='kaggle-processor',
    namespace='default',
    image='kaggle-processor:latest',
    arguments=['{{ dag_run.conf.get("dataset_name", "titanic") }}'],
    # Volume mount for persisting data back to host
    volumes=[k8s.V1Volume(
        name='data-volume',
        host_path=k8s.V1HostPathVolumeSource(path='/tmp/airflow-data', type='DirectoryOrCreate')
    )],
    volume_mounts=[k8s.V1VolumeMount(
        name='data-volume',
        mount_path='/app/data'
    )],
    # Kubernetes configuration
    image_pull_policy='Never',  # Use local image loaded with kind
    in_cluster=False,  # Connect from outside cluster
    config_file='/home/airflow/.kube/config',
    # Resource limits
    container_resources=k8s.V1ResourceRequirements(
        requests={'memory': '256Mi', 'cpu': '250m'},
        limits={'memory': '512Mi', 'cpu': '500m'}
    ),
    # Clean up pod after completion
    is_delete_operator_pod=True,
    get_logs=True,
    dag=dag,
)
