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

image = "devuser2021/sample-docker:latest"
command = "python3"
name ="app"
args ="/bd-fs-mnt/project_repo/code/test.py"
image_pull_policy = "Never"

resources=k8s.V1ResourceRequirements(limits={'cpu': '500m', 'memory':'4Gi'},requests={'cpu': '500m', 'memory':'4Gi'})

meta_name = 'k8s-pod-' + uuid.uuid4().hex
metadata = k8s.V1ObjectMeta(name=(meta_name),namespace="test", labels={"hpecp.hpe.com/dtap": "hadoop2","hpecp.hpe.com/fsmount": "test"})

container=k8s.V1Container(image=image, command=command, name=name, args=args,image_pull_policy=image_pull_policy,resources=resources)
spec=k8s.V1PodSpec(restart_policy="Never" , share_process_namespace = "true" , containers=[container])                
full_pod_spec = k8s.V1Pod( api_version ="v1",kind ="Pod", metadata=metadata, spec = spec)


python_task = KubernetesPodOperator(namespace='test',
                                    name="passing-python",
                                    in_cluster=True,
                                    is_delete_operator_pod=True,
                                    task_id="passing-task-python",
                                    get_logs=True,
                                    full_pod_spec=full_pod_spec,
                                    dag=dag
                                   )
python_task.set_upstream(start)
