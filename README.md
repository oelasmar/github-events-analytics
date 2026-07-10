🛠️ Fase 1: Setup Inicial y Dockerización del Core
El objetivo es levantar toda la infraestructura local metida en contenedores y dejar listos los servicios cloud gratuitos.

[ ] Repositorio en GitHub y Git Flow: Crea el repositorio, define la estructura de carpetas (/dags, /dbt_project, /src) y bloquea la rama main para forzar el uso de ramas feature/.

[ ] Entorno de Python con uv / poetry: Configura el entorno virtual local para el desarrollo de scripts y soporte del IDE.

[ ] Supabase Cloud Setup: * Crea el Bucket github-events-bronze en Supabase Storage.

Guarda las credenciales de conexión a Postgres y las API keys en un archivo .env local.

[ ] Infraestructura con Docker Compose: Configura un docker-compose.yml robusto que levante:

Apache Airflow (imagen oficial ligera o Astro CLI) mapeando los volúmenes de /dags.

Las dependencias necesarias para que Airflow comparta red con tus futuros scripts.

📥 Fase 2: Ingesta, Almacenamiento y Carga (El script de Python - EL)
Aquí construimos el script que moverá los datos, pero ya pensando en que será ejecutado de manera automática.

[ ] Script de Extracción (Capa Bronze): Desarrolla el script en Python que consulta la API de Eventos Públicos de GitHub y sube el archivo .json particionado por fecha (ej. ano=2026/mes=07/dia=01/events_xxx.json) a tu Bucket de Supabase Storage.

[ ] Script de Ingesta (Capa Silver - Raw): Añade la lógica para leer ese archivo JSON recién guardado (o el payload de la API) e insertarlo en formato raw (tipo de datos JSONB de Postgres) en la tabla raw.github_events de Supabase.

🎛️ Fase 3: Orquestación Local con Apache Airflow
Antes de pasar a dbt, dejamos el motor de ingesta automatizado y controlado por tiempo.

[ ] Diseño del DAG de Ingesta: Crea tu primer DAG en Airflow (dag_github_ingestion.py) con una frecuencia de ejecución (schedule) de cada 15 o 30 minutos.

[ ] Implementación de Tareas: Diseña el flujo utilizando PythonOperator (o DockerOperator si prefieres aislar el script):

Tarea 1 (extract_to_bronze): Llama a la API y guarda en Supabase Storage.

Tarea 2 (load_to_silver): Vuelca el JSONB en la tabla raw.github_events.

[ ] Validación en la interfaz de Airflow: Enciende tu entorno Docker, activa el DAG en la UI de Airflow y comprueba que se ejecuta sin errores y que las tareas se completan secuencialmente.

🏗️ Fase 4: Modelado de Datos con dbt (La Transformación - T)
Con la base de datos de Supabase recibiendo datos frescos de Airflow constantemente, toca estructurar la analítica.

[ ] Inicializar dbt-postgres: Inicializa el proyecto dentro de tu repositorio (dbt init). Configura el profiles.yml local apuntando a Supabase.

[ ] Capa de Staging (dbt): Crea modelos para desanidar el campo JSONB de raw.github_events usando la sintaxis nativa de Postgres (payload->>'action'), limpiar timestaps y renombrar a snake_case.

[ ] Estrategia Incremental: Configura tus modelos de Staging o Hechos como materialized='incremental' basándote en la columna created_at, garantizando que dbt solo procese datos nuevos en cada ejecución para ahorrar recursos.

[ ] Capa de Marts (Modelo Dimensional Kimball): Desarrolla los modelos finales:

dim_usuarios y dim_repositorios.

fct_eventos_github (Tabla de hechos conectada a las dimensiones mediante claves sustitutas o IDs).

🧪 Fase 5: Calidad de Datos, Documentación y Cierre del DAG
Aseguramos la robustez del modelo y conectamos dbt con el orquestador local.

[ ] Tests de dbt: Implementa tests de unicidad (unique), no nulos (not_null) e integridad referencial (relationships) en el archivo schema.yml.

[ ] Macros de dbt: Escribe alguna macro en Jinja útil para el proyecto (ej. limpieza de texto en nombres de repositorios o conversión de zonas horarias).

[ ] Cierre del bucle en Airflow: Integra dbt en tu DAG local de Airflow utilizando Cosmos (de Astronomer) o un BashOperator. Ahora el DAG completo hará:
Python Extract ➡️ Python Load ➡️ dbt run/test.

[ ] Documentación: Genera el catálogo de datos con dbt docs generate.

🚀 Fase 6: CI/CD Automatizado con GitHub Actions
El código de dbt y de los DAGs se automatiza para asegurar que los cambios no rompan la base de datos de Supabase.

[ ] Configurar GitHub Secrets: Sube de forma segura las credenciales de Supabase a los secretos del repositorio.

[ ] Workflow de CI (Pull Request / Slim CI): Crea el workflow que se dispara al abrir un PR. Debe ejecutar dbt build contra un esquema efímero en Supabase (ej. analytics_pr_12) y pasar los tests. Si todo es correcto, añade un paso de SQL para aplicar un DROP SCHEMA y limpiar Supabase.

[ ] Workflow de CD (Merge a Main): Configura el despliegue automático para que, al fusionar el código en main, GitHub Actions ejecute el dbt definitivo sobre el esquema final analytics de Supabase.

📊 Fase 7: Visualización y Negocio con Power BI
El escaparate final que consumirá los datos modelados por dbt desde la nube.

[ ] Conexión Limpia a Supabase: Conecta Power BI Desktop directamente al Postgres de Supabase apuntando única y exclusivamente al esquema analytics.

[ ] Modelado en Estrella Semántico: Importa tus dimensiones y hechos. Diseña el modelo de relaciones en Power BI sin tocar Power Query (toda la transformación ya se hizo en dbt).

[ ] Capa de Métricas (DAX): Desarrolla las medidas clave del negocio (ej. Porcentaje de Pull Requests aceptados, Evolución temporal de commits, Top usuarios más activos).

[ ] Diseño del Dashboard: Diseña un reporte visual ejecutivo e interactivo. Documenta en el README.md de tu repositorio capturas de este dashboard junto con el grafo de linaje (DAG) de dbt.

RULE 2: EXPERT GUIDE
¿Qué te parece esta distribución de las fases? Si estás de acuerdo, podemos empezar directamente redactando el archivo docker-compose.yml de la Fase 1 para dejar Airflow y tu entorno de desarrollo local perfectamente configurados.