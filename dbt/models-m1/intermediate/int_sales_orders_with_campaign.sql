with

sales_orders as (

    select * from {{ ref('stg_ecom__sales_orders') }}

),

campaign_events as (

    select * from {{ ref('stg_ecom__email_campaigns') }}
    where event_type = 'conversion'

),

campaign_join as (

    select
        so.*,
        ce.campaign_id,
        ce.customer_segment,
        ce.product_category,
        ce.ad_strategy,
        case 
            when ce.campaign_id is not null then 1 else 0
        end as is_campaign_conversion

    from sales_orders so
    left join campaign_events ce
        on so.sales_order_id = ce.order_id
)

select * from campaign_join
