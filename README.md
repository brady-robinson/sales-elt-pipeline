# Sales ELT Pipeline

## Overview

This project is a fully containerized, end-to-end ELT (Extract, Load, Transform) pipeline for sales analytics. It demonstrates how to ingest raw sales data from S3-compatible object storage (MinIO), stage and transform it in a PostgreSQL database using dbt, orchestrate the workflow with Apache Airflow, and visualize the results in a Streamlit dashboard. The entire stack runs locally using Docker Compose, and is designed for easy extension to production deployments.

---

## Architecture

**Components:**
- **MinIO**: S3-compatible object storage for raw CSV data.
- **Postgres**: Analytics database for staging and marts.
- **dbt**: Data transformation, testing, and documentation.
- **Apache Airflow**: Orchestration of the ELT pipeline.
- **Streamlit**: Web dashboard for analytics.
- **Docker Compose**: Local development and orchestration.

**Data Flow:**
1. **Raw CSV** is uploaded to MinIO (`raw/sales/sales.csv`).
2. **Ingestion script** downloads the CSV from MinIO and loads it into the `stg_sales` table in Postgres.
3. **dbt** transforms the staged data into analytics marts (e.g., `sales_summary`).
4. **Airflow DAG** orchestrates the above steps.
5. **Streamlit** queries the mart tables and displays analytics.

---

## Directory Structure

```
.
├── airflow/                # Airflow DAGs and configs
│   └── dags/
│       └── sales_pipeline.py
├── arch/                   # Architecture diagrams (add PNGs here)
├── dbt/                    # dbt project (models, seeds, profiles)
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_sales.sql
│   │   ├── marts/
│   │   │   └── sales_summary.sql
│   │   └── schema.yml
│   └── seeds/
│       └── sample_sales.csv
├── docker-compose.yml      # Main Docker Compose file
├── dockerfiles/            # Dockerfiles for custom containers
│   ├── Dockerfile.dbt
│   └── Dockerfile.streamlit
├── ingest/                 # Ingestion scripts
│   └── ingest_to_postgres.py
├── streamlit/              # Streamlit dashboard app
│   └── app.py
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Service Breakdown

### 1. Postgres
- Stores all raw, staging, and analytics data.
- Exposed on port `5432` for local access.
- Credentials: `airflow` / `airflow` (change for production).

### 2. MinIO
- S3-compatible object storage for raw data.
- Exposed on port `9000` (UI: http://localhost:9000).
- Credentials: `minioadmin` / `minioadmin` (change for production).
- Bucket: `raw`, Key: `sales/sales.csv`.

### 3. Airflow
- Orchestrates the ELT pipeline via a DAG (`sales_pipeline.py`).
- Web UI: http://localhost:8080 (user: `airflow` / `airflow`).
- DAG steps:
  1. Download CSV from MinIO and load to Postgres (`ingest_to_postgres.py`).
  2. Run dbt transformations (`dbt run`).
  3. Run dbt tests (`dbt test`).

### 4. dbt
- Handles all SQL transformations, tests, and documentation.
- Models:
  - `stg_sales`: Staging/cleaning of raw sales data.
  - `sales_summary`: Daily sales aggregates.
- Seeds: Sample CSV for demo/testing.
- Profiles configured for local Postgres.

### 5. Streamlit
- Simple analytics dashboard (http://localhost:8501).
- Connects to Postgres and visualizes sales summary data.
- Example: Time-series chart, top customers, data table.

---

## Setup & Usage

### Prerequisites
- Docker & Docker Compose
- (Optional) git, Python 3.11 for local tests

### 1. Clone the Repository
```bash
git clone <repo-url> sales-elt-pipeline
cd sales-elt-pipeline
```

### 2. Build & Start All Services
```bash
docker-compose up --build
```

### 3. Upload Sample Data to MinIO
- Open MinIO UI: http://localhost:9000
- Login: `minioadmin` / `minioadmin`
- Create bucket `raw` (if not exists)
- Upload `dbt/seeds/sample_sales.csv` as `sales/sales.csv`

### 4. Trigger the Airflow DAG
- Open Airflow UI: http://localhost:8080
- Login: `airflow` / `airflow`
- Find and trigger the `sales_pipeline` DAG

### 5. View the Dashboard
- Open Streamlit: http://localhost:8501
- If no data appears, ensure the pipeline ran and data is in `sales_summary`.

---

## dbt Project Details
- `dbt_project.yml`: Main dbt config
- `profiles.yml`: Connection to Postgres
- `models/staging/stg_sales.sql`: Cleans and types raw sales data
- `models/marts/sales_summary.sql`: Aggregates sales by day
- `models/schema.yml`: Tests (not_null, unique) and docs
- `seeds/sample_sales.csv`: Example data for local testing

---

## Ingestion Script
- `ingest/ingest_to_postgres.py`:
  - Downloads CSV from MinIO using `boto3`
  - Loads data into Postgres `stg_sales` table using `psycopg2`
  - Table is auto-created if not present
  - Environment variables control connection details

---

## Airflow DAG
- `airflow/dags/sales_pipeline.py`:
  - Task 1: PythonOperator runs ingestion script
  - Task 2: BashOperator runs `dbt run`
  - Task 3: BashOperator runs `dbt test`
  - All code and scripts are mounted into the Airflow container

---

## Streamlit Dashboard
- `streamlit/app.py`:
  - Connects to Postgres using SQLAlchemy
  - Reads from `sales_summary` table
  - Displays time-series chart and data table

---

## Dockerfiles
- `dockerfiles/Dockerfile.dbt`: Lightweight dbt container
- `dockerfiles/Dockerfile.streamlit`: Streamlit + dependencies

---

## CI/CD
- `.github/workflows/ci.yml`:
  - On push/PR: runs dbt tests in GitHub Actions
  - Installs dbt, runs `dbt deps`, `dbt seed`, `dbt run`, `dbt test`

---

## Security & Production Notes
- Change all default credentials for production
- Use Docker secrets or a vault for sensitive data
- Consider using Supabase for managed Postgres
- Add monitoring/logging as needed

---

## Troubleshooting
- **No data in dashboard?**
  - Check Airflow DAG logs for errors
  - Ensure sample CSV is uploaded to MinIO
  - Confirm Postgres is running and accessible
- **dbt errors?**
  - Check model SQL and schema.yml for issues
  - Validate connection details in `profiles.yml`
- **Container build issues?**
  - Ensure Docker is up to date
  - Rebuild with `docker-compose build --no-cache`

---

## Extending the Project
- Add new dbt models for more analytics
- Add Airflow tasks for additional data sources
- Enhance Streamlit dashboard with filters and charts
- Integrate with cloud storage or managed DBs

---

## License
MIT

---

## Author & Credits
- Project scaffolded by [Your Name]
- Inspired by modern data engineering best practices
