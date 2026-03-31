with campaign_summary as (
    select
        customer_segment,
        ad_strategy,
        product_category,
        count_if(event_type = 'email_opened') as email_opened,
        count_if(event_type = 'email_clicked') as emails_clicked,
        count_if(event_type = 'add_to_cart') as added_to_cart,
        count_if(event_type = 'conversion') as conversions,
        count(*) as total_events
    from {{ ref('stg_ecom__email_campaigns') }}
    group by
        customer_segment,
        ad_strategy,
        product_category
)

select
    customer_segment,
    ad_strategy,
    product_category,
    email_opened,
    emails_clicked,
    added_to_cart,
    conversions,
    round((emails_clicked / nullif(email_opened,0))*100,2) as click_through_rate_pct,
    round((added_to_cart / nullif(emails_clicked,0))*100,2) as add_to_cart_rate_pct,
    round((conversions / nullif(added_to_cart,0))*100,2) as conversion_rate_pct
from campaign_summary
order by conversion_rate_pct desc;
