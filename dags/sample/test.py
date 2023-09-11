import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator


def get_path(_path, step, _dir=None):
    up_path = os.sep.join(_path.split(os.sep)[:-step])
    if _dir is None:
        return up_path
    return os.path.join(up_path, _dir)


module_path = get_path(os.path.dirname(os.path.abspath(__file__)), 2)
sys.path.append(module_path)

from dags.dag_utils import common

DAG_NAME = 'SAMPLE_DAG_TEST'
dag_args = {
    'owner': 'my.park',
    'depends_on_past': False,
    'start_date': datetime.today() - timedelta(days=1),
    'email_on_failure': False,
    'email_on_retry': False
}

CRON_SCHEDULE = '@once'
dag = DAG(DAG_NAME,
          catchup=False,
          default_args=dag_args,
          schedule_interval=CRON_SCHEDULE,
          tags=["test"],
          is_paused_upon_creation=False  # dag 가 최초에 추가될 때 바로 실행할 것인지 여부
          )


def test_script():
    print(f"CALL_{DAG_NAME}")
    num = common.sample_common_fn(123)
    return num


sample_task = PythonOperator(
    task_id='sample-task',
    dag=dag,
    python_callable=test_script,
    execution_timeout=timedelta(minutes=5),
    retries=0
)

dummy_task = DummyOperator(
    task_id='dummy-task',
    dag=dag
)

sample_task >> dummy_task