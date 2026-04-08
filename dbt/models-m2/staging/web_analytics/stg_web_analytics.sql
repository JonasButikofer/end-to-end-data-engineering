with 

source as (
    select * from {{ source('web_analytics', 'web_analytics_raw') }}
),

renamed as (

    select 
        customer_id::int as customer_id,
        product_id::int as product_id,
        session_id::string as session_id,
        page_url::string as page_url,
        event_type::string as event_type,
        event_timestamp::timestamp_ntz as event_timestamp,
        _loaded_at::timestamp_ntz as loaded_at,
        _file_name::string as file_name,
        current_timestamp() as dbt_loaded_at
    from source
)

select * from renamed