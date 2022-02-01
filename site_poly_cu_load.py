from datetime import timedelta, datetime

# [START import_module]
# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor
from airflow.utils.dates import days_ago

# [END import_module]

# [START default_args]
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'max_active_runs': 1,
    'retries': 3
}
# [END default_args]

# [START instantiate_dag]

dag = DAG(
    'demo_spark',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    tags=['example']
)

# spark = open(
#     "example_spark_kubernetes_operator_pi.yaml").read()

submit = SparkKubernetesOperator(
    task_id='demo_spark_submit',
    namespace="data-engineering",
    application_file="site_poly_cu_load.yaml",
    kubernetes_conn_id="kubernetes_in_cluster",
    do_xcom_push=True,
    dag=dag,
    api_group="sparkoperator.hpe.com",
    enable_impersonation_from_ldap_user=False
)

sensor = SparkKubernetesSensor(
    task_id='demo_spark_monitor',
    namespace="data-engineering",
    application_name="{{ task_instance.xcom_pull(task_ids='demo_spark_submit')['metadata']['name'] }}",
    kubernetes_conn_id="kubernetes_in_cluster",
    dag=dag,
    api_group="sparkoperator.hpe.com",
    attach_log=True
)

submit >> sensor
