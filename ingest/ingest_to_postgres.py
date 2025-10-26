#!/usr/bin/env python3
"""
Simple MinIO -> Postgres CSV loader.
Place a CSV at bucket 'raw', key 'sales/sales.csv' with header:
id,order_id,customer_id,amount,created_at
"""
import os
import boto3
import psycopg2
import csv
from io import StringIO

MINIO_ENDPOINT = os.getenv(
    "MINIO_ENDPOINT", "http://minio:9000"
)
MINIO_ACCESS = os.getenv("MINIO_ACCESS", "minioadmin")
MINIO_SECRET = os.getenv("MINIO_SECRET", "minioadmin")
BUCKET = "raw"
OBJECT_KEY = "sales/sales.csv"

PG_HOST = os.getenv("PG_HOST", "postgres")
PG_PORT = int(os.getenv("PG_PORT", 5432))
PG_DB = os.getenv("PG_DB", "sales")
PG_USER = os.getenv("PG_USER", "airflow")
PG_PASS = os.getenv("PG_PASS", "airflow")


def download_csv():
    print(f"Connecting to MinIO at {MINIO_ENDPOINT} with access key {MINIO_ACCESS}...")
    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS,
        aws_secret_access_key=MINIO_SECRET,
    )
    print(f"Attempting to download {OBJECT_KEY} from bucket {BUCKET}...")
    obj = s3.get_object(Bucket=BUCKET, Key=OBJECT_KEY)
    body = obj["Body"].read().decode("utf-8")
    print(f"Downloaded {len(body)} bytes from MinIO.")
    return body


def load_to_postgres(csv_text):
    print(
        f"Connecting to Postgres at {PG_HOST}:{PG_PORT}, db={PG_DB}, user={PG_USER}..."
    )
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
    )
    cur = conn.cursor()
    print("Ensuring raw.sales table exists...")

    # Create the raw.sales table
    cur.execute(
        """
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE TABLE IF NOT EXISTS raw.sales (
        id integer PRIMARY KEY,
        order_id text,
        customer_id text,
        amount double precision,
        created_at timestamp
    );
    """
    )

    # Create a temporary table for staging
    print("Creating temporary table for staging...")
    cur.execute(
        """
    CREATE TEMP TABLE temp_sales (
        id integer,
        order_id text,
        customer_id text,
        amount double precision,
        created_at timestamp
    ) ON COMMIT DROP;
    """
    )

    # Load data into the temporary table
    f = StringIO(csv_text)
    reader = csv.reader(f)
    headers = next(reader)  # skip header
    print(f"CSV headers: {headers}")
    f.seek(0)
    next(f)  # skip header
    print("Loading data into temporary table...")
    cur.copy_expert(
        "COPY temp_sales(id,order_id,customer_id,amount,created_at) "
        "FROM STDIN WITH CSV",
        f,
    )

    # Upsert data into raw.sales
    print("Upserting data into raw.sales...")
    cur.execute(
        """
    INSERT INTO raw.sales (id, order_id, customer_id, amount, created_at)
    SELECT id, order_id, customer_id, amount, created_at
    FROM temp_sales
    ON CONFLICT (id) DO UPDATE
    SET order_id = EXCLUDED.order_id,
        customer_id = EXCLUDED.customer_id,
        amount = EXCLUDED.amount,
        created_at = EXCLUDED.created_at;
    """
    )

    conn.commit()
    print("Data upserted and committed.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    csv_text = download_csv()
    load_to_postgres(csv_text)
    print("Ingestion complete.")
