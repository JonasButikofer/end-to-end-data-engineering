with

duped as (

    select * from {{ ref('base_ecom__email_campaigns') }}
    union all
    select * from {{ ref('base_ecom__email_mktg_new') }}

),

deduped as (

    select 
        * 
        
    from duped
    QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY event_date) = 1

),
ranked_rows AS (
    SELECT *,
            ROW_NUMBER() OVER (PARTITION BY order_id, event_type ORDER BY event_date DESC) AS rn
    FROM deduped

),
ranked_deduped as (
    
    SELECT *
    FROM ranked_rows
    WHERE rn = 1 
),
final as (

    select
        event_id,
        campaign_id,
        split_part(campaign_id, '~', 1) as customer_segment,
        split_part(campaign_id, '~', 2) as product_category,
        split_part(campaign_id, '~', 3) as ad_strategy,
        event_date,
        event_type,
        customer_id,
        order_id,
        case 
            when order_id is null then 0 else 1
        end as is_converted
    from ranked_deduped
)

select * from final
