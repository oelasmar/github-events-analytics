# GitHub Analytics - Modern Data Stack Pipeline

Pipeline de *Analytics Engineering* end-to-end diseñado bajo la arquitectura Medallion y herramientas del Modern Data Stack (MDS). Realiza el consumo de eventos semi-estructurados de la API de GitHub mediante **Python** y construye un Data Lakehouse/Warehouse en **Supabase (PostgreSQL)** estructurado en capas (*Bronze*, *Silver* y *Gold*), realizando la transformación de la capa analítica con **dbt**. El pipeline completo se orquesta con **Apache Airflow**, usando **GitHub Actions** para la automatización  **Slim CI / CD**.

![dbt](https://img.shields.io/badge/dbt-1.8.0-FF694B?style=for-the-badge&logo=https://cdn.simpleicons.org/dbt/white)
![Apache Airflow](https://img.shields.io/badge/Apache_Airflow-2.9.0-017CEE?style=for-the-badge&logo=https://cdn.simpleicons.org/apacheairflow/white)
![PostgreSQL](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=https://cdn.simpleicons.org/postgresql/white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=https://cdn.simpleicons.org/python/white)
![uv](https://img.shields.io/badge/uv-Package_Manager-DE5FE9?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?style=for-the-badge&logo=https://cdn.simpleicons.org/githubactions/white)

## Arquitectura

### 1. Diagrama End-to-End (Medallion)

```mermaid
graph LR
    subgraph "Medallion Architecture (Supabase)"
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

```mermaid
graph TD


    subgraph "Entorno Local & Desarrollo (Sandbox)"
        DEV_CODE[Código SQL / dbt Local] -->|uv run dbt build| LOCAL_DB[( dbt_DEV_analytics)]
    end
```



```mermaid
graph TD

    subgraph "Continuous Integration (CI - Pull Request)"
        PR[PR a 'dev'] -->|Triggers Workflow| CI_ACTION[GitHub Actions CI]
        CI_ACTION -->|dbt build| EPHEMERAL_DB[(analytics_pr_X_*)]
        CI_ACTION -->|Data Tests & Quality Checks| TEST_RESULT{¿Tests OK?}
        TEST_RESULT --> CLEANUP[Cleanup Python Script: DROP SCHEMA CASCADE]
    end

```


```mermaid
graph TD

    subgraph "Continuous Deployment (CD - Merge to Main)"
        MERGE[Merge a 'master'] -->|Triggers Workflow| CD_ACTION[GitHub Actions CD]
        CD_ACTION -->|dbt build| PROD_DB[(prod_analytics)]
    end
```


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



## Características principales
* **Entorno Determinista con `uv`:** Uso de `uv` como gestor de paquetes de Python garantizando builds reproducibles tanto en local como en los runners de GitHub Actions (`uv run dbt deps` / `uv run dbt build`).
* **Arquitectura Medallion en Supabase:**
  * **Bronze (`storage`):** Ingesta cruda de eventos semi-estructurados en JSON desde la API de GitHub mediante Python.
  * **Silver (`raw`):** Limpieza, de-duplicación, casting de tipos y filtrado inicial procesado con Python.
  * **Gold (`analytics`):** Tablas de hechos incrementales (`fct_github_events`) y dimensiones (`dim_github_users`, `dim_github_repositories`) modeladas con dbt.
* **Orquestación Containerizada con Docker & Airflow:** Programación modular (cada 5 minutos) de las tareas de extracción, carga e invocación de transformaciones (dbt) mediante Apache Airflow desplegado localmente en contenedores Docker (`Docker Compose`).
* **Modelos Incrementales en Fact Table:** Configuración de `fct_github_events` como tabla incremental para optimizar los tiempos de ejecución y minimizar costes de cómputo al procesar únicamente los eventos nuevos.
* **Calidad de Datos Automatizada:** Más de 14 data tests integrados (`not_null`, `unique`, `relationships` y reglas de negocio validadas con `dbt_expectations`).
* **Slim CI con Esquemas Efímeros & Autocleanup:** Generación dinámica de esquemas aislados por Pull Request (ej. `analytics_pr_9_%`). Incluye un script que limpia los esquemas al finalizar el CI.
* **Despliegue Continuo (CD) & Custom Schemas:** Macros personalizadas en dbt para derivar automáticamente esquemas por entorno y publicar cambios directamente a producción (`prod_src` y `prod_analytics`) tras el merge en `main`.

* **Seguridad y Gestión de Credenciales:** Aislamiento de variables sensibles mediante archivos `.env` en desarrollo local y la inyección segura de credenciales (`SUPABASE_DB_*`) usando **GitHub Repository Secrets** en los flujos de CI/CD.



## Resultados

### 1. Almacenamiento

#### - Capa Bronze

![Bronze Layer](/images/bronze_layer.png)

#### - Capa Silver

![Silver Layer](/images/silver_layer.png)

#### - Gold

![Gold Layer](/images/gold_layer.png)

#### - Gold --- *fct_github_events*

![Gold Layer 1](/images/gold_layer_1.png)

#### - Gold --- *dim_github_users*

![Gold Layer 2](/images/gold_layer_2.png)

#### - Gold --- *dim_github_repositories*

![Gold Layer 3](/images/gold_layer_3.png)


### 2. Orquestación

#### - DAG

![Airflow](/images/airflow_dag.png)

#### - Esquema

![Airflow Schema](/images/airflow_dag_schema.png)

#### - Ejecución

![Airflow Execution](/images/airflow_dag_execution.png)


