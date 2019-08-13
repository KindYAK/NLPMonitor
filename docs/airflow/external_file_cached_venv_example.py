"""
Code that goes along with the Airflow tutorial located at:
https://github.com/apache/airflow/blob/master/airflow/example_dags/tutorial.py
"""
from airflow import DAG
from datetime import datetime, timedelta
from external_file_example.my_package import some_complicated_stuff

from PythonVirtualenvCachedOperator import PythonVirtualenvCachedOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 7, 25),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('external_cached_venv_example', default_args=default_args, schedule_interval=timedelta(days=1))

test_env_op = PythonVirtualenvCachedOperator(
    task_id="op1",
    python_callable=some_complicated_stuff,
    python_version="3.6",
    dag=dag,
    requirements=[
        "xlrd==1.2.0",
    ]
)
