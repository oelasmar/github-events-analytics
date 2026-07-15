import subprocess
import logging
from datetime import datetime, timedelta
from airflow.decorators import dag, task

PROYECTO_PATH = "/opt/airflow"

# Configuración por defecto para las tareas
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

@dag(
    dag_id="github_events_ingestion",
    default_args=default_args,
    description="Pipeline de ingesta de eventos de GitHub: Bronze & Silver",
    schedule="*/30 * * * *",  # Ejecución cada 30 minutos
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["github", "bronze_layer", "silver_layer"]
)

def github_events():

    @task
    def extract_bronze():

        command = f"uv run python ./src/extract_bronze.py"
        result = subprocess.run(command, shell=True, cwd=PROYECTO_PATH, check=True)
        
    # "ds" --> contiene la fecha lógica exacta de esa ejecución formateada como texto en YYYY-MM-DD.    
    @task
    def transform_silver(ds=None):

        command = f"uv run python ./src/transform_silver.py --execution-date {ds}"
        result = subprocess.run(command, shell=True, cwd=PROYECTO_PATH, check=True)
        
    extract_bronze() >> transform_silver()

github_events()