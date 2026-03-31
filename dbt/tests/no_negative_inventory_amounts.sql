-- Test: ensure inventory quantities are never negative
--
-- Returns rows where quantity < 0 (test fails if any rows returned)

select
    quantity
from
    {{ ref('stg_adventure_db__inventory') }}
where
    quantity < 0
