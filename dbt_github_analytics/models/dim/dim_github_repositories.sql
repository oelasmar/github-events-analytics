
WITH github_events AS (
    SELECT * FROM {{ ref('src_github_events') }}
    WHERE repository_id IS NOT NULL
),

repositories AS (
    SELECT distinct
        repository_id,
        repository_name,
        SPLIT_PART(repository_name, '/', 1)             AS repository_owner,
        SPLIT_PART(repository_name, '/', 2)             AS repository_short_name,
        org_name,
        CASE 
            WHEN org_name IS NOT NULL THEN 'Organization'
            ELSE 'User Account'
        END                                             AS repository_type
    FROM github_events
)

SELECT * FROM repositories   
