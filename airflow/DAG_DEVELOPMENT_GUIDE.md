# Airflow DAG Development Guide

This guide explains how to create scalable, cloud-ready Airflow DAGs using KubernetesPodOperator for data processing tasks.

## Architecture Overview

Our setup provides:
- **Local Development**: Test with kind (Kubernetes in Docker)
- **Cloud Deployment**: Deploy to GKE, EKS, or AKS with zero code changes
- **Isolated Execution**: Each task runs in its own Kubernetes pod
- **Scalable**: Kubernetes handles resource management and auto-scaling

## Prerequisites

### 1. Install kind (Local Kubernetes)
```bash
# Download and install kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
mkdir -p ~/.local/bin && mv ./kind ~/.local/bin/
export PATH=$PATH:~/.local/bin

# Create local cluster
kind create cluster --name airflow-dev
```

### 2. Verify Setup
```bash
# Check kind cluster
kubectl cluster-info --context kind-airflow-dev

# Check Airflow is running
docker compose ps
```

## Creating a New Processing DAG

### Step 1: Create Your Processor

1. **Write your processing script** in `src/` directory
2. **Create a Dockerfile** for your processor:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY ../pyproject.toml ./
RUN pip install --no-cache-dir \
    your-required-packages

# Copy source code
COPY ../src/ ./src/
ENV PYTHONPATH=/app/src

# Create data directory
RUN mkdir -p /app/data

# Set entrypoint
ENTRYPOINT ["python", "/app/src/your_module/your_script.py"]
```

### Step 2: Build and Load Docker Image

```bash
# Build from airflow directory
cd airflow
docker build -f Dockerfile.your-processor -t your-processor:latest .

# Load into kind cluster
kind load docker-image your-processor:latest --name airflow-dev
```

### Step 3: Create the DAG

Create a new DAG file in `airflow/dags/`:

```python
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
    'your_processing_dag',
    default_args=default_args,
    description='Description of your processing task',
    schedule_interval=None,  # Manual trigger or set schedule
    catchup=False,
    tags=['your-tags', 'kubernetes'],
)

# Main processing task
processing_task = KubernetesPodOperator(
    task_id='your_processor_pod',
    name='your-processor',
    namespace='default',
    image='your-processor:latest',
    arguments=['{{ dag_run.conf.get("param_name", "default_value") }}'],
    
    # Volume mounts for data persistence
    volumes=[k8s.V1Volume(
        name='data-volume',
        host_path=k8s.V1HostPathVolumeSource(
            path='/tmp/airflow-data', 
            type='DirectoryOrCreate'
        )
    )],
    volume_mounts=[k8s.V1VolumeMount(
        name='data-volume',
        mount_path='/app/data'
    )],
    
    # Kubernetes configuration
    image_pull_policy='Never',  # For local development
    in_cluster=False,
    config_file='/home/airflow/.kube/config',
    
    # Resource limits
    container_resources=k8s.V1ResourceRequirements(
        requests={'memory': '256Mi', 'cpu': '250m'},
        limits={'memory': '1Gi', 'cpu': '1000m'}
    ),
    
    # Cleanup and logging
    is_delete_operator_pod=True,
    get_logs=True,
    dag=dag,
)
```

## Configuration Patterns

### 1. Environment-Specific Settings

```python
import os

# Detect environment
is_production = os.getenv('AIRFLOW_ENV') == 'production'

# Configure based on environment
if is_production:
    image_pull_policy = 'Always'
    config_file = None  # Use in-cluster config
    in_cluster = True
    image_registry = 'gcr.io/your-project/'
else:
    image_pull_policy = 'Never'
    config_file = '/home/airflow/.kube/config'
    in_cluster = False
    image_registry = ''

processing_task = KubernetesPodOperator(
    # ... other params ...
    image=f'{image_registry}your-processor:latest',
    image_pull_policy=image_pull_policy,
    in_cluster=in_cluster,
    config_file=config_file,
)
```

### 2. Dynamic Parameters

```python
# Pass parameters from DAG run configuration
processing_task = KubernetesPodOperator(
    # ... other params ...
    arguments=[
        '{{ dag_run.conf.get("dataset_name", "default") }}',
        '{{ dag_run.conf.get("output_format", "csv") }}',
        '--date={{ ds }}',  # Airflow execution date
    ],
    env_vars={
        'PROCESSING_MODE': '{{ dag_run.conf.get("mode", "batch") }}',
        'LOG_LEVEL': '{{ var.value.log_level }}',  # Airflow variable
    }
)
```

### 3. Multiple Tasks with Dependencies

```python
# Task 1: Data validation
validate_task = KubernetesPodOperator(
    task_id='validate_data',
    name='data-validator',
    image='your-validator:latest',
    # ... other config ...
    dag=dag,
)

# Task 2: Data processing
process_task = KubernetesPodOperator(
    task_id='process_data',
    name='data-processor',
    image='your-processor:latest',
    # ... other config ...
    dag=dag,
)

# Task 3: Generate report
report_task = KubernetesPodOperator(
    task_id='generate_report',
    name='report-generator',
    image='your-reporter:latest',
    # ... other config ...
    dag=dag,
)

# Define dependencies
validate_task >> process_task >> report_task
```

## Cloud Deployment

### Moving to Production (GKE/EKS/AKS)

1. **Push Docker images to container registry:**
```bash
# Tag and push to your registry
docker tag your-processor:latest gcr.io/your-project/your-processor:latest
docker push gcr.io/your-project/your-processor:latest
```

2. **Update DAG configuration:**
```python
# Change image reference
image='gcr.io/your-project/your-processor:latest',
image_pull_policy='Always',
in_cluster=True,  # Use in-cluster service account
config_file=None,
```

3. **Deploy Airflow to Kubernetes cluster:**
- Use Helm chart or Kubernetes manifests
- Configure proper RBAC permissions
- Set up persistent volumes for data

## Best Practices

### 1. Resource Management
```python
# Set appropriate resource limits
container_resources=k8s.V1ResourceRequirements(
    requests={
        'memory': '512Mi',  # Minimum required
        'cpu': '250m'       # 0.25 CPU cores
    },
    limits={
        'memory': '2Gi',    # Maximum allowed
        'cpu': '1000m'      # 1 CPU core
    }
)
```

### 2. Error Handling
```python
# Configure retries and timeouts
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}
```

### 3. Monitoring and Logging
```python
# Enable log collection
get_logs=True,

# Add labels for monitoring
labels={
    'app': 'data-processing',
    'version': 'v1.0',
    'team': 'data-team'
}
```

### 4. Security
```python
# Use service accounts
service_account_name='data-processor-sa',

# Avoid secrets in code - use Kubernetes secrets
env_vars={
    'API_KEY': {'secret_name': 'api-secrets', 'secret_key': 'api-key'}
}
```

## Testing

### 1. Local Testing
```bash
# Test DAG syntax
docker exec airflow-airflow-scheduler-1 python /opt/airflow/dags/your_dag.py

# Test DAG execution
docker exec airflow-airflow-scheduler-1 airflow dags test your_processing_dag 2024-01-01

# Check DAG in UI
# Navigate to http://localhost:8080
```

### 2. Validate Kubernetes Resources
```bash
# Check if pods are created
kubectl get pods

# Check pod logs
kubectl logs <pod-name>

# Describe pod for troubleshooting
kubectl describe pod <pod-name>
```

## Troubleshooting

### Common Issues

1. **Image Not Found:**
   - Ensure image is loaded: `kind load docker-image your-processor:latest --name airflow-dev`
   - Check image name matches exactly in DAG

2. **Permission Errors:**
   - Verify volume mount paths exist: `mkdir -p /tmp/airflow-data`
   - Check Kubernetes RBAC permissions in production

3. **Resource Issues:**
   - Monitor resource usage: `kubectl top pods`
   - Adjust resource limits in DAG

4. **Network Issues:**
   - Verify kind cluster networking
   - Check if Airflow can access Kubernetes API

### Debugging Commands
```bash
# Check DAG import errors
airflow dags list-import-errors

# View task logs
airflow tasks logs your_processing_dag your_processor_pod 2024-01-01

# Test Kubernetes connection
kubectl cluster-info

# Check Airflow configuration
airflow config list
```

## File Structure

Your project should look like this:
```
project/
├── src/                          # Your processing code
│   └── your_module/
│       └── processor.py
├── airflow/
│   ├── dags/
│   │   └── your_processing_dag.py
│   ├── Dockerfile.processor      # Docker image for your processor
│   └── docker-compose.yml       # Airflow setup
└── pyproject.toml               # Python dependencies
```

This structure keeps the project root clean while maintaining proximity between Airflow components.