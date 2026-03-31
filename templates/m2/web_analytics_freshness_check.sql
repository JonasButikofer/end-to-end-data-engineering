{#
    Custom test: verify that the most recent event in the web analytics
    staging model is no more than 24 hours old. This is a data freshness
    check that works independently of dbt's built-in source freshness.

    The test fails (returns a row) if the most recent event_timestamp
    is more than 24 hours old.

    Students: implement this test. The query should return rows only when
    the freshness check FAILS (i.e., when data is stale). If data is
    fresh, the query returns zero rows and the test passes.
#}

-- TODO: Write a query that returns a row when the most recent
--       event_timestamp in stg_web_analytics is more than 24 hours old.
--
-- Hint: Use DATEDIFF and MAX to compare the most recent timestamp
--       against CURRENT_TIMESTAMP().
--
-- Example structure:
--   select 1
--   from (
--       select max(event_timestamp) as most_recent
--       from {{ ref('stg_web_analytics') }}
--   ) freshness
--   where datediff('hour', freshness.most_recent, current_timestamp()) > 24

select 1 where 1 = 0  -- placeholder: always passes until you implement
