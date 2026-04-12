with 

clickstream as (
    select * from {{ ref('stg_web_analytics') }}
),

customers as (
    select * from {{ ref('stg_adventure_db__customers') }}
),

enriched as (

    select
        cs.session_id,
        cs.customer_id,
        cs.product_id,
        cs.page_url,
        cs.event_type,
        cs.event_timestamp,
        cs.loaded_at,
        cs.dbt_loaded_at,
        c.full_name          as customer_name,
        c.email_address      as customer_email,
        c.city               as customer_city,
        c.state_province     as customer_state,
        c.country_region     as customer_country,
        c.postal_code        as customer_postal_code
    from clickstream cs
    left join customers c
        on cs.customer_id::string = c.customer_id

)


select * from enriched

