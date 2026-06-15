# Airflow DAG for Part 1. Same pipeline as pipeline.py but as 5 separate tasks,
# each one saving to a temp file and passing the path to the next.
# Set DEFENCE_CRON (e.g. "0 9 20 6 *") to run it on a schedule, otherwise it
# only runs when you trigger it from the UI.
import os
import sys
from datetime import datetime

import pandas as pd
from airflow import DAG
try:
    from airflow.operators.python import PythonOperator              # Airflow 2
except ImportError:
    from airflow.providers.standard.operators.python import PythonOperator  # Airflow 3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from part1_batch import config, reader, validator, processor, writer

TMP = os.path.join(config.OUTPUT_DIR, "_tmp")
os.makedirs(TMP, exist_ok=True)


def step_read(**_):
    p = os.path.join(TMP, "raw.csv")
    reader.read().to_csv(p, index=False)
    return p

def step_validate(ti, **_):
    df = validator.validate(pd.read_csv(ti.xcom_pull(task_ids="read"), dtype=str))
    p = os.path.join(TMP, "validated.csv"); df.to_csv(p, index=False)
    return p

def step_process(ti, **_):
    df = processor.process(pd.read_csv(ti.xcom_pull(task_ids="validate"), dtype=str))
    p = os.path.join(TMP, "processed.csv"); df.to_csv(p, index=False)
    return p

def step_backup_check(ti, **_):
    df = validator.backup_check(pd.read_csv(ti.xcom_pull(task_ids="process")))
    p = os.path.join(TMP, "final.csv"); df.to_csv(p, index=False)
    return p

def step_write(ti, **_):
    return writer.write(pd.read_csv(ti.xcom_pull(task_ids="backup_check")))


with DAG(
    dag_id="nashville_batch",
    start_date=datetime(2025, 1, 1),
    schedule=os.getenv("DEFENCE_CRON") or None,
    catchup=False,
    tags=["part1", "batch"],
) as dag:
    read = PythonOperator(task_id="read", python_callable=step_read)
    validate = PythonOperator(task_id="validate", python_callable=step_validate)
    process = PythonOperator(task_id="process", python_callable=step_process)
    backup_check = PythonOperator(task_id="backup_check", python_callable=step_backup_check)
    write = PythonOperator(task_id="write", python_callable=step_write)

    read >> validate >> process >> backup_check >> write
