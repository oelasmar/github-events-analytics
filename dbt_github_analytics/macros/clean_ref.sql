{% macro clean_ref(column_name) %}
    CASE
        WHEN {{ column_name }} LIKE 'refs/heads/%' THEN REPLACE({{ column_name }}, 'refs/heads/', '')
        WHEN {{ column_name }} LIKE 'refs/tags/%'  THEN REPLACE({{ column_name }}, 'refs/tags/', '')
        ELSE {{ column_name }}
    END
{% endmacro %}