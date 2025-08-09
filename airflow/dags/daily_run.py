import boto3
from airflow.models.dag import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from docker.types import Mount

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

def get_ec2_id(ec2_client):
    response = ec2_client.describe_instances()

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:

            instance_name = 'N/A'
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        if instance_name == 'argusmaximus':
                            instance_id = instance['InstanceId']
                            return instance_id
    raise Exception('Theres no instance id with argusmaximus name')

def shutdown_ec2_instance():
    try:
        
        ec2_client = boto3.client('ec2', region_name='sa-east-1') 
        instance_id = get_ec2_id(ec2_client)
        print(f"Encontrado o ID da instância: {instance_id}")

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

    data_mount = Mount(
        target="/app/argus/data", 
        source="/home/ec2-user/argus/ArgusMaximus/argus/data", 
        type="bind"
    )

    models_mount = Mount(
        target="/app/argus/models",
        source ="/home/ec2-user/argus/ArgusMaximus/argus/models",
        type='bind'
    )

    task_run_argus = DockerOperator(
        task_id='run_etls',
        image='argus-project:latest',  
        api_version='auto',
        auto_remove=True,
        command="python scripts/main.py", 
        working_dir="/app/argus",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        mount_tmp_dir=False,
        mounts=[data_mount, models_mount]
    )


    task_shutdown_instance = PythonOperator(
        task_id='shutdown_ec2_instance',
        python_callable=shutdown_ec2_instance,
        trigger_rule='all_done'
    )

    [task_run_argus] >> task_shutdown_instance