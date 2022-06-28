import logging

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
from kubernetes.client import models as k8s
import uuid

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

#python_task = KubernetesPodOperator(namespace='test',
#                                    image="devuser2021/sample-docker:latest",
#                                    cmds=["python3", "/bd-fs-mnt/TenantShare/repo/code/test.py" ,"-c"],
#                                    labels={"hpecp.hpe.com/dtap": "hadoop2","hpecp.hpe.com/fsmount": "test"},
#                                    full_pod_spec={"restartPolicy": "Never","shareProcessNamespace": "true"},
#                                    resources={'limit_memory': "4Gi", 'limit_cpu': "500m"},
#                                    name="passing-python",
#                                    in_cluster=True,
#                                    is_delete_operator_pod=True,
#                                    task_id="passing-task-python",
#                                    get_logs=True,
#                                    dag=dag
#                                   )

meta_name = 'k8s-pod-' + uuid.uuid4().hex
metadata = k8s.V1ObjectMeta(name=(meta_name))
full_pod_spec = k8s.V1Pod(
    metadata=metadata,
  )

python_task = KubernetesPodOperator(namespace='test',
                                    name="passing-python",
                                    in_cluster=True,
                                    is_delete_operator_pod=True,
                                    task_id="passing-task-python",
                                    get_logs=True,
                                    full_pod_spec=full_pod_spec,
                                    pod_template_file="test.yaml",
                                    dag=dag
                                   )
python_task.set_upstream(start)
