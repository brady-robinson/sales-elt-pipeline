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

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
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
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS,
        aws_secret_access_key=MINIO_SECRET
    )
    obj = s3.get_object(Bucket=BUCKET, Key=OBJECT_KEY)
    body = obj['Body'].read().decode('utf-8')
    return body

def load_to_postgres(csv_text):
    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stg_sales (
        id integer PRIMARY KEY,
        order_id text,
        customer_id text,
        amount double precision,
        created_at timestamp
    );
    """)
    f = StringIO(csv_text)
    reader = csv.reader(f)
    headers = next(reader)  # skip header
    # Use COPY for speed
    f.seek(0)
    next(f)  # skip header
    cur.copy_expert("COPY stg_sales(id,order_id,customer_id,amount,created_at) FROM STDIN WITH CSV", f)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    csv_text = download_csv()
    load_to_postgres(csv_text)
    print("Ingestion complete.")
