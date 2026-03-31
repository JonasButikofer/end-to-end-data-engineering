with

intentional_test_failure as (

    -- Adding a 2nd conversion event for order_id = 44330, which already has one
    select 
        parse_json('{
            "event_id": "this-is-a-fake-event-id",
            "event_type": "conversion", 
            "order_id": 44330
        }') as RAW

),

source as (

    select * from {{ source('ecom_source', 'email_campaign_raw') }}

    -- comment out the next line to remove the test violation:
    -- union all select * from intentional_test_failure

),

renamed as (

    select
        raw:campaign_id::string     as campaign_id,
        raw:event_id::string        as event_id,
        TO_TIMESTAMP(
            raw:event_date::string, 
            'DD-Mon-YYYY HH12.MI AM'
            )                       as event_date,
        raw:event_type::string      as event_type,
        raw:customer_id::string     as customer_id,
        raw:order_id::string        as order_id,
        raw:product_id::string      as product_id
    from source

)

select * from renamed
