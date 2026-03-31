-- Test: ensure preferred vendors have credit ratings >= 1
--
-- Returns rows where a preferred vendor has insufficient credit rating
-- (test fails if any rows returned)

select
    *
from
    {{ ref('stg_adventure_db__vendors') }}
where
    preferred_vendor_status = true
and
    credit_rating < 1
