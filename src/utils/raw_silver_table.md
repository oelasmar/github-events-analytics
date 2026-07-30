#### 1. Crear el esquema analítico raw 

```sql
CREATE SCHEMA IF NOT EXISTS raw;
```

#### 2. Crear la tabla para la ingesta del JSONB

```sql
CREATE TABLE IF NOT EXISTS raw.github_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE,         
    event_type VARCHAR(100) NOT NULL,           
    payload JSONB NOT NULL,                      
    loaded_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);
```