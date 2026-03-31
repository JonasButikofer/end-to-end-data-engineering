-- Test: verify that sell_end_date is fully null in the products table
--
-- This confirms that no product currently has an end-of-sale date set.
-- Returns rows where sell_end_date is NOT null (test fails if any rows returned)

select
    sell_end_date
from
    {{ ref('stg_adventure_db__products') }}
where
    sell_end_date is not null
