# Airflow Orchestration

This directory contains all Airflow-related configuration and DAGs for orchestrating the data stack.

## Quick Start

1. Navigate to the airflow directory:
   ```bash
   cd airflow
   ```

2. Start Airflow services:
   ```bash
   docker-compose up -d
   ```

3. Access Airflow UI:
   - URL: http://localhost:8080
   - Username: admin
   - Password: admin

## Directory Structure

- `dags/` - Airflow DAGs for data processing workflows
- `logs/` - Airflow execution logs
- `plugins/` - Custom Airflow plugins
- `config/` - Airflow configuration files
- `docker-compose.yml` - Docker services definition
- `.env` - Environment variables

## Services

- **airflow-webserver**: Web UI (port 8080)
- **airflow-scheduler**: Task scheduler
- **airflow-worker**: Celery worker for task execution
- **postgres**: Metadata database
- **redis**: Message broker for Celery

## Data Access

The main application's `data/` and `src/` directories are mounted to `/opt/airflow/data` and `/opt/airflow/src` respectively, allowing DAGs to access your datasets and code.