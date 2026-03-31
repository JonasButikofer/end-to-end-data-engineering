{#
    Custom test: verify that the web analytics staging model
    contains at least 50 rows. This is a smoke test to confirm
    data is actually flowing from the API through the Prefect
    pipeline into Snowflake.

    The test fails (returns a row) if fewer than 50 rows exist.
#}

select 1
from (
    select count(*) as row_count
    from {{ ref('stg_web_analytics') }}
) counts
where counts.row_count < 50
