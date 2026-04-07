with

sales_orders as (

    select * from {{ ref('int_sales_orders_with_campaign') }}

),

customers as (

    select * from {{ ref('stg_adventure_db__customers') }}

),

joined as (

    select
        so.sales_order_id,
        so.order_date,
        so.total_due,
        so.sub_total,
        so.customer_id,
        so.campaign_id,
        so.is_campaign_conversion,
        c.country_region,
        c.city,
        c.state_province
    from sales_orders so
    left join customers c
        on so.customer_id = c.customer_id

),

last_30_days as (

    select *
    from joined
    where order_date >= dateadd(day, -30, current_date())

)

select * from last_30_days
