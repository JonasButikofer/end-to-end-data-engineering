with

source as (

    select * from {{ source('new_mktg', 'email_mktg_raw') }}

),

renamed as (

    select
        REPLACE(
            raw:campaign_id::string,
            ' ',
            '')                      as campaign_id,
        raw:EventID::string          as event_id,
        TO_TIMESTAMP(
            raw:eventDate::string, 
            'DD-Mon-YYYY HH12.MI AM'
            )                        as event_date,
        LOWER(raw:eventType::string) as event_type,
        raw:customer_id::string      as customer_id,
        raw:orderId::string          as order_id,
        raw:ProductId::string        as product_id
    from source

)

select * from renamed
