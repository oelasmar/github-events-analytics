{{
    config(
        materialized = 'incremental',
        unique_key = 'event_id',
        on_schema_change = 'append_new_columns',
        schema = 'analytics'
    )
}}

WITH src_github_events AS (
    SELECT * 
    FROM {{ ref('src_github_events') }}

    {% if is_incremental() %}
        WHERE event_created_at > (SELECT MAX(event_created_at) FROM {{ this }})
    {% endif %}
),

events as (
SELECT
    event_id,
    actor_id,
    repository_id,
    event_type,
    is_public,
    ref,
    ref_type,
    COALESCE(pusher_type, 'unknown')     AS pusher_type,
    push_id,
    -- pr_number,
    -- pr_title,
    -- pr_merged,
    -- pr_creator,
    event_created_at,
    loaded_at                           
FROM src_github_events
)

select * from events
