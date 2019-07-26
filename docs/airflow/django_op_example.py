"""
Code that goes along with the Airflow tutorial located at:
https://github.com/apache/airflow/blob/master/airflow/example_dags/tutorial.py
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonVirtualenvOperator, PythonOperator
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

# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag)

t2 = BashOperator(
    task_id='sleep',
    bash_command='sleep 5',
    retries=3,
    dag=dag)

templated_command = """
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
        echo "{{ params.my_param }}"
    {% endfor %}
"""

t3 = BashOperator(
    task_id='templated',
    bash_command=templated_command,
    params={'my_param': 'Parameter I passed in'},
    dag=dag)


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


def test_env_op_callable():
    import xlrd
    print(xlrd.__version__)
    return xlrd.__version__


test_env_op = PythonVirtualenvOperator(
    task_id="test_env_op",
    python_callable=test_env_op_callable,
    python_version="3.6",
    dag=dag,
    requirements=[
        "xlrd==1.2.0",
    ]
)

def python_test():
    return 5 / 253345

python_op = PythonOperator(
    task_id="python_op",
    python_callable=python_test,
    dag=dag,
)

python_op >> test_env_op >> django_op >> t1 >> [t2, t3]
