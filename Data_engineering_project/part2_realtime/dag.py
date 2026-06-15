# Airflow DAG for Part 2. Checks the input folder every minute and processes
# whatever is waiting there. Basically the Airflow version of watcher.py.
import os
import sys
from datetime import datetime

from airflow import DAG
try:
    from airflow.operators.python import PythonOperator                 # Airflow 2
    from airflow.sensors.filesystem import FileSensor
except ImportError:
    from airflow.providers.standard.operators.python import PythonOperator   # Airflow 3
    from airflow.providers.standard.sensors.filesystem import FileSensor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from part2_realtime import config, pipeline


def process_waiting_files(**_):
    for name in sorted(os.listdir(config.INPUT_DIR)):
        path = os.path.join(config.INPUT_DIR, name)
        if os.path.isfile(path) and name.lower().endswith(config.ALLOWED_EXTENSIONS):
            pipeline.process_file(path)


with DAG(
    dag_id="realtime_folder",
    start_date=datetime(2025, 1, 1),
    schedule="* * * * *",          # every minute
    catchup=False,
    max_active_runs=1,
    tags=["part2", "realtime"],
) as dag:
    # wait for a file to appear (don't fail the run if nothing is there)
    wait = FileSensor(
        task_id="wait_for_file",
        filepath=config.INPUT_DIR,
        poke_interval=15,
        timeout=50,
        mode="reschedule",
        soft_fail=True,
    )
    process = PythonOperator(task_id="process", python_callable=process_waiting_files)

    wait >> process
