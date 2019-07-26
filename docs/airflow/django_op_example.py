"""
Code that goes along with the Airflow tutorial located at:
https://github.com/apache/airflow/blob/master/airflow/example_dags/tutorial.py
"""
from airflow import DAG
from DjangoOperator import DjangoOperator
from datetime import datetime, timedelta


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

dag = DAG('django_op_example', default_args=default_args, schedule_interval=timedelta(days=1))

def test():
    from mainapp.models import Corpus
    import random
    Corpus.objects.create(name="Delete Later " + str(random.randint(0, 10000000)))
    import xlrd
    print(xlrd.__version__)
    return xlrd.__version__


django_op = DjangoOperator(
    task_id="test_corpus_create",
    python_callable=test,
    dag=dag
)
