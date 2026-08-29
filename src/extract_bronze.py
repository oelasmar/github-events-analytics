import os
import json
from datetime import datetime
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno locales (.env)
load_dotenv()

# Variables
GITHUB_API_URL = "https://api.github.com/events"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Opcional, pero recomendado para evitar rate limits

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "github-events-bronze"

# Funciones
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Las credenciales de Supabase no están configuradas en el .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_github_events() -> list:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
        
    print(f"[{datetime.now()}] Consultando la API de GitHub...")
    response = requests.get(GITHUB_API_URL, headers=headers, timeout=15)
    
    # Validar códigos de respuesta habituales o rate limits
    response.raise_for_status()
    
    events = response.json()
    print(f"[{datetime.now()}] Se han extraído {len(events)} eventos correctamente.")
    return events

def upload_to_supabase_bronze(events_data: list):
    supabase = get_supabase_client()
    
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    timestamp = int(now.timestamp())
    
    storage_path = f"{year}/{month}/{day}/github_events_{timestamp}.json"
    temp_filename = f"temp_events_{timestamp}.json"
    
    with open(temp_filename, "w", encoding="utf-8") as f:
        json.dump(events_data, f, indent=2)
        
    print(f"[{now}] Subiendo datos a Supabase en la ruta: {storage_path}...")
    
    try:
        with open(temp_filename, "rb") as file_to_upload:
            supabase.storage.from_(BUCKET_NAME).upload(
                path=storage_path,
                file=file_to_upload,
                file_options={"content-type": "application/json"}
            )
        print(f"[{datetime.now()}] Subida completada con éxito.")
    except Exception as e:
        print(f"Error crítico al subir los datos a Supabase Storage: {e}")
        raise e
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


def main():
    try:
        data = fetch_github_events()
        if data:
            upload_to_supabase_bronze(data)
        else:
            print("No se encontraron eventos en esta ejecución.")
    except Exception as e:
        print(f"La ejecución del script de extracción ha fallado: {e}")
        exit(1)

if __name__ == "__main__":
    main()