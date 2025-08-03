import boto3
from airflow.models.dag import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import docker 
from docker.types import Mount



default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

def shutdown_ec2_instance():
    """
    Usa o boto3 para obter o ID da instância atual e desligá-la.
    Isso requer que a instância EC2 tenha uma IAM Role com a permissão ec2:StopInstances.
    """
    try:
        instance_id = boto3.utils.get_instance_metadata()['instance-id']
        print(f"Encontrado o ID da instância: {instance_id}")
        
        ec2_client = boto3.client('ec2', region_name='us-east-1') 
        
        print(f"Enviando comando para desligar a instância {instance_id}...")
        ec2_client.stop_instances(InstanceIds=[instance_id])
        print("Comando de desligamento enviado com sucesso.")
        
    except Exception as e:
        print(f"Erro ao tentar desligar a instância: {e}")
        raise

with DAG(
    dag_id='daily_argus_job',
    default_args=default_args,
    schedule_interval='5 0 * * *',  
    catchup=False,
    tags=['argus', 'docker', 'ec2'],
) as dag:

    resultado_mount = Mount(
        target="/app/argus/data", 
        source="/home/ec2-user/argus/ArgusMaximus", 
        type="bind"
    )


    task_run_etls = DockerOperator(
        task_id='run_etls',
        image='argus-project:latest',  
        api_version='auto',
        auto_remove=True,
        command="python argus/scripts/run_etls.py", 
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        mount_tmp_dir=False,
        mounts=[resultado_mount]
    )

    task_train_models = DockerOperator(
        task_id='train_models',
        image='argus-project:latest', 
        api_version='auto',
        auto_remove=True,
        command="python argus/scripts/train_models.py", 
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        mount_tmp_dir=False,
        mounts=[resultado_mount]
    )

    task_shutdown_instance = PythonOperator(
        task_id='shutdown_ec2_instance',
        python_callable=shutdown_ec2_instance,
        trigger_rule='all_done'
    )

    [task_run_etls >> task_train_models] >> task_shutdown_instance