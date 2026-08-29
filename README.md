# GitHub Analytics - Modern Data Stack Pipeline

Pipeline de *Analytics Engineering* end-to-end diseñado bajo la arquitectura Medallion y herramientas del Modern Data Stack (MDS). Realiza el consumo de eventos semi-estructurados de la API de GitHub mediante **Python** y construye un Data Lakehouse/Warehouse en **Supabase (PostgreSQL)** estructurado en capas (*Bronze*, *Silver* y *Gold*), realizando la transformación de la capa analítica con **dbt**. El pipeline completo se orquesta con **Apache Airflow**, usando **GitHub Actions** para la automatización  **Slim CI / CD**.

![dbt](https://img.shields.io/badge/dbt-1.8.0-FF694B?style=for-the-badge&logo=https://cdn.simpleicons.org/dbt/white)
![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-2.9.0-017CEE?style=for-the-badge&logo=https://cdn.simpleicons.org/apacheairflow/white)
![PostgreSQL](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=https://cdn.simpleicons.org/postgresql/white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=https://cdn.simpleicons.org/python/white)
![uv](https://img.shields.io/badge/uv-Package_Manager-DE5FE9?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?style=for-the-badge&logo=https://cdn.simpleicons.org/githubactions/white)

--- 

## Arquitectura

### 1. Diagrama End-to-End (Medallion)

```mermaid
graph LR
    subgraph " "
        GH_API[GitHub REST API] -->|Raw_Ingestion_Python| BRONZE[(Bronze Layer Storage: github-events-bronze)]
        BRONZE -->|Transformation_Python| SILVER[(Silver Layer: github_events)]
        SILVER -->|dbt_Models| GOLD[(Gold Layer: dim_users, dim_repos, fct_events)]
    end

    AIRFLOW[Apache Airflow Orchestrator]

    AIRFLOW -.-> BRONZE
    AIRFLOW -.-> SILVER
    AIRFLOW -.-> GOLD

```


### 2. Diagrama CI/CD

##### Entorno Local (Desarrollo)

```mermaid
graph TD


    subgraph " "
        DEV_CODE[Código SQL / dbt Local] -->|uv run dbt build| LOCAL_DB[( dbt_DEV_analytics)]
    end
```

##### CI - Pull Request a entorno DEV

```mermaid
graph TD

    subgraph " " 
        PR[PR a 'dev'] -->|Triggers Workflow| CI_ACTION[GitHub Actions CI]
        CI_ACTION -->|dbt build| EPHEMERAL_DB[(analytics_pr_X_*)]
        CI_ACTION -->|Data Tests & Quality Checks| TEST_RESULT{¿Tests OK?}
        TEST_RESULT --> CLEANUP[Cleanup Python Script: DROP SCHEMA CASCADE]
    end

```

##### CD - Merge a entorno PROD

```mermaid
graph TD

    subgraph " "
        MERGE[Merge a 'master'] -->|Triggers Workflow| CD_ACTION[GitHub Actions CD]
        CD_ACTION -->|dbt build| PROD_DB[(prod_analytics)]
    end
```

---

## Resultados obtenidos

### 1. Almacenamiento

### - Capa Bronze

![Bronze Layer](/images/bronze_layer.png)

### - Capa Silver

![Silver Layer](/images/silver_layer.png)

### - Capa Gold

![Gold Layer](/images/gold_layer.png)

#### - Capa Gold --- *fct_github_events*

![Gold Layer 1](/images/gold_layer_1.png)

### - Capa Gold --- *dim_github_users*

![Gold Layer 2](/images/gold_layer_2.png)

### - Capa Gold --- *dim_github_repositories*

![Gold Layer 3](/images/gold_layer_3.png)


### 2. Orquestación

### - DAG

![Airflow](/images/airflow_dag.png)

### - Esquema

![Airflow Schema](/images/airflow_dag_schema.png)

### - Ejecución

![Airflow Execution](/images/airflow_dag_execution.png)

---

## Tech Stack

| Área | Tecnologías Utilizadas |
| :--- | :--- |
| **Ingestion** | Python 3.11+, REST APIs |
| **Orchestration** | Apache Airflow |
| **Data Architecture** | Medallion Architecture (Bronze ➔ Silver ➔ Gold) |
| **Data Transformation** | dbt-core (v1.8+), Jinja, dbt_expectations |
| **Data Warehouse** | Supabase (PostgreSQL) |
| **CI-CD & Automation** | GitHub Actions (Slim CI / CD Workflows) |
| **Environment & Tooling** | `uv` , `psycopg2` |
| **Version Control** | Git / GitHub (Git Flow: `feature/*` ➔ `dev` ➔ `main`) |

---

## Justificación del Stack

- **Medallion Architecture**: Permite aislar el dato crudo en Bronze (auditoría sin pérdida de origen), Silver (calidad estándar) y Gold donde se crean modelos estrella optimizados para consumo analítico.
<br>

- **uv vs pip/poetry**: Elegido por su rapidez y garantización de reproducir de forma exacta de dependencias.
<br>

- **dbt + Supabase (Postgres)**: dbt permite aplicar buenas prácticas de ingeniería de software (control de versiones, tests, documentación modular, Jinja) directamente sobre el Data Warehouse. Además, Supabase nos sirve como Data Warehouse y almacenamiento para el *staging* del dato.
<br>

- **Airflow**: Herramienta líder en la industria para la orquestación de pipelines.
<br>

- **Slim CI con Esquemas Efímeros**: En lugar de probar contra el entorno dev completo, se generan esquemas efímeros por Pull Request (analytics_pr_X) que se destruyen automáticamente tras pasar las pruebas. Esto reduce drásticamente el coste computacional y el desorden en la base de datos.

---

## Características principales
-  **Entorno Determinista con `uv`:** Uso de `uv` como gestor de paquetes de Python garantizando builds reproducibles tanto en local como en los runners de GitHub Actions (`uv run dbt deps` / `uv run dbt build`).
<br>

- **Arquitectura Medallion en Supabase:**
  * **Bronze (`storage`):** Ingesta cruda de eventos semi-estructurados en JSON desde la API de GitHub mediante Python.
  * **Silver (`raw`):** Limpieza, de-duplicación, casting de tipos y filtrado inicial procesado con Python.
  * **Gold (`analytics`):** Tablas de hechos incrementales (`fct_github_events`) y dimensiones (`dim_github_users`, `dim_github_repositories`) modeladas con dbt.
  <br>

- **Orquestación Containerizada con Docker & Airflow:** Programación modular (cada 5 minutos) de las tareas de extracción, carga e invocación de transformaciones (dbt) mediante Apache Airflow desplegado localmente en contenedores Docker (`Docker Compose`).
<br>

- **Modelos Incrementales en Fact Table:** Configuración de `fct_github_events` como tabla incremental para optimizar los tiempos de ejecución y minimizar costes de cómputo al procesar únicamente los eventos nuevos.
<br>

- **Calidad de Datos Automatizada:** Más de 14 data tests integrados (`not_null`, `unique`, `relationships` y reglas de negocio validadas con `dbt_expectations`).
<br>

- **Slim CI con Esquemas Efímeros & Autocleanup:** Generación dinámica de esquemas aislados por Pull Request (ej. `analytics_pr_9_%`). Incluye un script que limpia los esquemas al finalizar el CI.
<br>

-  **Despliegue Continuo (CD) & Custom Schemas:** Macros personalizadas en dbt para derivar automáticamente esquemas por entorno y publicar cambios directamente a producción (`prod_src` y `prod_analytics`) tras el merge en `main`.
<br>

- **Seguridad y Gestión de Credenciales:** Aislamiento de variables sensibles mediante archivos `.env` en desarrollo local y la inyección segura de credenciales (`SUPABASE_DB_*`) usando **GitHub Repository Secrets** en los flujos de CI/CD.
