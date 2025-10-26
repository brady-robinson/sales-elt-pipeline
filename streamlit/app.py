import os
import pandas as pd
import streamlit as st
import sqlalchemy

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://airflow:airflow@postgres:5432/sales"
)
engine = sqlalchemy.create_engine(DATABASE_URL)

st.title("Sales Summary Dashboard")

with engine.connect() as conn:
    df = pd.read_sql("select * from sales_summary order by day desc limit 100", conn)

    if df.empty:
        st.warning("No data in sales_summary. Run the pipeline.")
    else:
        st.line_chart(df.set_index("day")["total_amount"])
        st.dataframe(df)
