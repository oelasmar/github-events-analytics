WITH github_events AS (
    SELECT * FROM {{ ref('src_github_events') }}
    WHERE actor_id IS NOT NULL
),

users AS (
    SELECT
        actor_id                                        AS user_id,
        actor_username                                  AS username,
        CASE 
            WHEN actor_username LIKE '%[bot]' THEN TRUE 
            ELSE FALSE 
        END                                             AS is_bot
    FROM github_events
)

select * from users