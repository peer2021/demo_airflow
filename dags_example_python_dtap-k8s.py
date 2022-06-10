import logging

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import \
    KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta


# log = logging.getLogger(__name__)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.utcnow(),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'kubernetes_dtap', default_args=default_args,
    schedule_interval=timedelta(minutes=10), tags=['example'])

start = DummyOperator(task_id='run_this_first', dag=dag)

python_task = KubernetesPodOperator(namespace='test',
                                    image="devuser2021/sample-docker:latest",
                                    cmds=["python", "test.py" ,"-c"],
                                    labels={"hpecp.hpe.com/dtap": "hadoop2"},
                                    resources={'limit_memory': "4Gi", 'limit_cpu': "500m"},
                                    name="passing-python",
                                    is_delete_operator_pod=True,
                                    task_id="passing-task-python",
                                    get_logs=True,
                                    dag=dag
                                    )


python_task.set_upstream(start)
