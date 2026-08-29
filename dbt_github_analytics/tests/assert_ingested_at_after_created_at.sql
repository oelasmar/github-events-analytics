-- Este test falla si la fecha de ingesta en BBDD es anterior a la fecha real en que ocurrió el evento en GitHub.
SELECT
    event_id,
    event_created_at,
    loaded_at
FROM {{ ref('fct_github_events') }}
WHERE loaded_at < event_created_at
