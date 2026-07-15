import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client, ClientOptions
import argparse
import sys

# Configuración básica de logs
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", stream=sys.stdout)

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "github-events-bronze"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Ingesta de Bronze a Silver Raw.")
    parser.add_argument(
        "--execution-date", 
        type=str, 
        help="Fecha lógica de ejecución (Formato: YYYY-MM-DD)",
        default=None
    )
    return parser.parse_args()

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Faltan las variables SUPABASE_URL o SUPABASE_KEY en el archivo .env")
        
    # Le indicamos al cliente que trabaje sobre el esquema 'raw'
    options = ClientOptions(schema="raw")
    return create_client(SUPABASE_URL, SUPABASE_KEY, options=options)

def get_latest_file_path(supabase: Client, execution_date: datetime) -> str:
    year = execution_date.strftime("%Y")
    month = execution_date.strftime("%m")
    day = execution_date.strftime("%d")
    
    # 1. Definimos la ruta de la carpeta donde están los archivos de ese día
    folder_path = f"{year}/{month}/{day}"
    
    logging.info(f"Escaneando el bucket en la ruta exacta de ejecución: {folder_path}...")
    
    try:
        # Pasamos la ruta de la carpeta al parámetro path
        response = supabase.storage.from_(BUCKET_NAME).list(
            path=folder_path,
            options={
                "limit": 100, 
                "sortBy": {"column": "name", "order": "desc"}
            }
        )
        
        if not response or len(response) == 0:
            raise FileNotFoundError(f"No se encontraron archivos en la ruta: {folder_path}")
            
        files = [f for f in response if f.get('id') is not None]
        
        if not files:
            raise FileNotFoundError(f"No se encontraron archivos JSON válidos en la ruta: {folder_path}")
            
        latest_file_name = files[0]['name']
        detected_path = f"{folder_path}/{latest_file_name}"
        logging.info(f"Archivo detectado -> {detected_path}")
        return detected_path
            
    except Exception as e:
        logging.error(f"Error al listar archivos en la ruta {folder_path}: {e}")
        raise e

def load_json_from_storage(supabase: Client, file_path: str) -> list:
    logging.info(f"Descargando archivo desde Storage: {file_path}...")
    try:
        response_bytes = supabase.storage.from_(BUCKET_NAME).download(file_path)
        # Parseamos los bytes descargados directamente a una lista/diccionario de Python
        return json.loads(response_bytes.decode('utf-8'))
    except Exception as e:
        logging.error(f"Error al descargar el archivo del bucket: {e}")
        raise e

def insert_events_to_postgres(supabase: Client, events: list):
    logging.info(f"Preparando la ingesta de {len(events)} eventos.")
    
    records_to_insert = []
    for event in events:
        records_to_insert.append({
            "event_id": str(event.get("id")),
            "event_type": event.get("type"),
            "payload": event
        })
        
    try:
        # Quitamos el .schema("raw") de aquí
        response = supabase.table("github_events") \
            .upsert(records_to_insert, on_conflict="event_id") \
            .execute()
            
        logging.info(f"Ingesta completada.")
    except Exception as e:
        logging.error(f"Error al insertar datos en Postgres: {e}")
        raise e

def main():
    logging.info("---- Iniciando proceso de carga a Capa Silver - Raw ----")
    
    # 1. Capturar los argumentos de la consola (siempre vendrá la fecha correcta)
    args = parse_arguments()
    execution_date = datetime.strptime(args.execution_date, "%Y-%m-%d")
    logging.info(f"Fecha de ejecución lógica de Airflow: {args.execution_date}")

    supabase = get_supabase_client()
    
    try:
        # 3. Pasar la fecha calculada a la función del storage
        latest_file = get_latest_file_path(supabase, execution_date)
        logging.info(f"Último archivo detectado: {latest_file}")
        
        # 4. Descargar y parsear el JSON
        events_data = load_json_from_storage(supabase, latest_file)
        
        # 5. Insertar los datos en Postgres
        insert_events_to_postgres(supabase, events_data)
        
        logging.info("=== Proceso de carga de la capa Silver finalizado con éxito ===")
    except Exception as e:
        logging.critical(f"La ejecución del pipeline de carga ha fallado: {e}")

if __name__ == "__main__":
    main()