🛠️ Fase 1: Setup Inicial y Dockerización del Core
El objetivo es levantar toda la infraestructura local metida en contenedores y dejar listos los servicios cloud gratuitos.

[X] Repositorio en GitHub y Git Flow: Crea el repositorio, define la estructura de carpetas (/dags, /dbt_project, /src) y bloquea la rama main para forzar el uso de ramas feature/.

[X] Entorno de Python con uv / poetry: Configura el entorno virtual local para el desarrollo de scripts y soporte del IDE.

[X] Supabase Cloud Setup: * Crea el Bucket github-events-bronze en Supabase Storage.

Guarda las credenciales de conexión a Postgres y las API keys en un archivo .env local.

[X] Infraestructura con Docker Compose: Configura un docker-compose.yml robusto que levante:

Apache Airflow (imagen oficial ligera o Astro CLI) mapeando los volúmenes de /dags.

Las dependencias necesarias para que Airflow comparta red con tus futuros scripts.

📥 Fase 2: Ingesta, Almacenamiento y Carga (El script de Python - EL)
Aquí construimos el script que moverá los datos, pero ya pensando en que será ejecutado de manera automática.

[X] Script de Extracción (Capa Bronze): Desarrolla el script en Python que consulta la API de Eventos Públicos de GitHub y sube el archivo .json particionado por fecha (ej. ano=2026/mes=07/dia=01/events_xxx.json) a tu Bucket de Supabase Storage.

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

PROBLEMAS

1. Al guardar por carpetas de fecha que pasa si entiendo, pero que ocurre si el extract se ejecuta a las 23:59 del dia 12 y la capa silver a las 00:01 del dia 13?

Opción A: La solución definitiva con Airflow (Contexto de Ejecución)
Cuando implementes Airflow, este problema desaparece por completo. Airflow no utiliza la hora del reloj del servidor (datetime.now()); utiliza variables de contexto llamadas data_interval_start (o la clásica execution_date).

Si el DAG corresponde a la ventana de las 23:00 a las 00:00:

Airflow sabe que esa tarea pertenece lógicamente al día 12.

Airflow le pasará exactamente la misma fecha como parámetro tanto al script de Extract como al de Silver (por ejemplo, a través de variables de entorno o argumentos de terminal).

Tu script de Silver no calculará el día actual con now(), sino que recibirá un parámetro diciendo: "Procesa la carpeta del día 12". Así, da igual si el script se ejecuta a las 00:01, a las 03:00 o tres días después; la idempotencia está garantizada.







Así funcionará tu flujo de CI/CD:
[ Rama feature/mi-modelo ] ──────────► [ Pull Request (CI) ] ──────────► [ Merge a main (CD) ]
          │                                      │                                    │
    Ejecuta en DEV:                        Ejecuta en STAGING:                  Ejecuta en PROD:
   Esquema de la tarea                    Esquema efímero del PR              Esquema definitivo
 (ej. dbt_initial_setup)                  (ej. analytics_pr_12)                 (ej. analytics)
          │                                      │                                    │
          ▼                                      ▼                                    ▼
   Supabase Cloud                         Supabase Cloud                       Supabase Cloud

   
1. En tu máquina local (Entorno DEV)
Trabajas en tu rama feature/initial-setup o similares.

En tu archivo .env local tienes definido DBT_SCHEMA=dbt_desarrollo (o el nombre de tu feature).

Cada vez que haces dbt run en tu terminal, dbt crea y actualiza las tablas dentro de Supabase Cloud pero aisladas en ese esquema de desarrollo (dbt_desarrollo). No rompes nada de producción.

2. Al abrir el Pull Request (Entorno STAGING / CI)
Cuando subes tu rama a GitHub y abres un Pull Request hacia main, se dispara automáticamente un Workflow de GitHub Actions.

Este workflow instala Python y dbt, lee tus credenciales secretas de Supabase y ejecuta:

Bash
dbt build --vars "{schema_override: analytics_pr_${{ github.event.number }}}"
La magia del CI: dbt creará un esquema temporal en tu Supabase llamado, por ejemplo, analytics_pr_12 (usando el número de tu PR). Ejecutará allí todos los modelos y pasará los dbt test de calidad de datos.

El borrado: Si todos los tests pasan con éxito, el propio workflow lanza un comando SQL (DROP SCHEMA ... CASCADE) para borrar ese esquema efímero de Supabase y no consumir espacio. El PR recibe el "check verde" de aprobado.

3. Al hacer Merge a main (Entorno PROD / CD)
Una vez fusionado el código en la rama main, se dispara el segundo workflow de GitHub Actions.

Este workflow ejecuta el dbt definitivo apuntando al esquema productivo final (por ejemplo, analytics).

Al ejecutar un dbt run de producción, tus tablas de hechos y dimensiones finales se actualizan de forma incremental, listas para que Power BI consuma los datos limpios.

¿Por qué esta estructura es una genialidad para tu portfolio?
Porque le demuestra a cualquier equipo técnico que sabes trabajar con Slim CI (integración continua ligera) en la nube sin incurrir en costes extras de infraestructura, y que tratas el código de datos con el mismo rigor que si fuera software de aplicación.

Con esto claro y tu archivo .env configurado, ¿pasamos a escribir el docker-compose.yml para levantar Apache Airflow localmente y cerrar por completo la Fase 1?