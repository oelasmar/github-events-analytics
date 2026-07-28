from datetime import datetime, timedelta
from airflow.decorators import dag
from airflow.providers.docker.operators.docker import DockerOperator
import os

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

@dag(
    dag_id="github_events_ingestion_docker",
    default_args=default_args,
    description="Pipeline de ingesta de eventos de GitHub: Bronze & Silver, con Docker",
    schedule="*/30 * * * *",  # Ejecución cada 30 minutos
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["github", "bronze_layer", "silver_layer", "docker"]
)

def github_events_docker():

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    github_token = os.getenv("GITHUB_TOKEN")

    db_host = os.getenv("SUPABASE_DB_HOST")
    db_user = os.getenv("SUPABASE_DB_USER")
    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    db_name = os.getenv("SUPABASE_DB_NAME")
    db_port = os.getenv("SUPABASE_DB_PORT")


    extract_bronze = DockerOperator(
        task_id="extract_bronze",
        image="github-events-app:latest",      
        command="uv run python ./src/extract_bronze.py",
        auto_remove="success",                   
        network_mode="bridge",                 
        docker_url="unix://var/run/docker.sock", 
        mount_tmp_dir=False,
        environment={                          
            "SUPABASE_URL": supabase_url,
            "SUPABASE_KEY": supabase_key,
            "GITHUB_TOKEN": github_token,
        }
    )

    transform_silver = DockerOperator(
        task_id="transform_silver",
        image="github-events-app:latest",
        command="uv run python ./src/transform_silver.py --execution-date {{ ds }}",
        auto_remove="success",
        network_mode="bridge",
        docker_url="unix://var/run/docker.sock",
        mount_tmp_dir=False,
        environment={
            "SUPABASE_URL": supabase_url,
            "SUPABASE_KEY": supabase_key,
            "GITHUB_TOKEN": github_token,
        }
    )

    # 3. dbt Models Execution (Marts / Analytics)
    dbt_run = DockerOperator(
        task_id="dbt_run",
        image="github-events-app:latest",  # O tu imagen donde tengas dbt instalado
        command="uv run dbt run --project-dir . --profiles-dir .",
        auto_remove="success",
        network_mode="bridge",
        docker_url="unix://var/run/docker.sock",
        mount_tmp_dir=False,
        environment={
            "DB_HOST": db_host,
            "DB_USER": db_user,
            "DB_PASSWORD": db_password,
            "DB_NAME": db_name,
            "DB_PORT": db_port,
        },
    )

    # 4. dbt Quality Tests
    dbt_test = DockerOperator(
        task_id="dbt_test",
        image="github-events-app:latest",
        command="uv run dbt test --project-dir . --profiles-dir .",
        auto_remove="success",
        network_mode="bridge",
        docker_url="unix://var/run/docker.sock",
        mount_tmp_dir=False,
        environment={
            "DB_HOST": db_host,
            "DB_USER": db_user,
            "DB_PASSWORD": db_password,
            "DB_NAME": db_name,
            "DB_PORT": db_port,
        },
    )

    # Flujo de ejecución lineal ELT
    extract_bronze >> transform_silver >> dbt_run >> dbt_test

github_events_docker()