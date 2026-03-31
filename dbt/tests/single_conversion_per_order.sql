-- Test: ensure no order has more than one conversion event
--
-- Each order should have at most one 'conversion' event in the email
-- campaign data. Returns orders with multiple conversions (test fails
-- if any rows returned).

with conversion_events as (

    select
        event_type,
        order_id
    from {{ ref('stg_ecom__email_campaigns') }}
    where event_type = 'conversion'

),

count_per_order as (

    select
        order_id,
        count(*) as event_count
    from conversion_events
    group by order_id

)

select * from count_per_order where event_count > 1
