with campaign_sales_summary as (
    select
        campaign_id,
        customer_segment,
        ad_strategy,
        product_category,
        count(distinct sales_order_id) as total_orders,
        avg(total_due) as avg_order_value,
        sum(total_due) as total_revenue
    from {{ ref('int_sales_orders_with_campaign') }}
    group by
        campaign_id,
        customer_segment,
        ad_strategy,
        product_category
)

select
    campaign_id,
    customer_segment,
    ad_strategy,
    product_category,
    total_orders,
    total_revenue,
    avg_order_value
from campaign_sales_summary
order by total_revenue desc;
