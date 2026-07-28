WITH raw_github_events as (
    SELECT * FROM {{source('github', 'github_events')}}
)

select
    id,
    event_id,
    event_type,
    payload->'org'->>'login'                     AS org_name,
    payload->'repo'->>'name'                    AS repository_name,
    payload->'repo'->>'url'                     AS repository_url,
    (payload->'repo'->>'id')::bigint            AS repository_id,
    payload->'actor'->>'login'                  AS actor_username,
    (payload->'actor'->>'id')::bigint           AS actor_id,
    (payload->>'created_at')::timestamp         AS event_created_at,
    (payload->>'public')::boolean               AS is_public,
    payload->'payload'->>'ref'                  AS ref,
    payload->'payload'->>'full_ref'             AS full_ref,
    payload->'payload'->>'ref_type'             AS ref_type,
    payload->'payload'->>'pusher_type'          AS pusher_type,
    payload->'payload'->>'master_branch'        AS master_branch,
    (payload->'payload'->>'push_id')::bigint    AS push_id,
    -- payload->'payload'->>'head'                 AS head_commit_sha,
    -- payload->'payload'->>'before'               AS before_commit_sha,
    loaded_at
from raw_github_events