with

source as (

    select * from {{ source('real_time', 'chat_logs_raw') }}

),

renamed as (

    select
        raw:_id::string                         as chat_id,
        raw:customer_id::int                    as customer_id,
        raw:sales_order_id::int                 as sales_order_id,
        raw:product_id::int                     as product_id,
        raw:order_date::timestamp               as order_date,
        raw:chat_start_time::timestamp          as chat_start_time,
        raw:chat_completion_time::timestamp     as chat_completion_time,
        raw:ticket_channel::string              as ticket_channel,
        raw:ticket_type::string                 as ticket_type,
        raw:ticket_subject::string              as ticket_subject,
        raw:ticket_description::string          as ticket_description,
        raw:ticket_priority::string             as ticket_priority,
        raw:ticket_status::string               as ticket_status,
        raw:resolution::string                  as resolution,
        raw:customer_satisfaction_rating::int   as customer_satisfaction_rating,
        to_timestamp(raw:last_modified::bigint / 1000) as last_modified
    from source

)

select * from renamed
