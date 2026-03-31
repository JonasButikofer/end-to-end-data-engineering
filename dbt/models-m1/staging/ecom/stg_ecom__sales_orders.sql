with

base as (

    select * from {{ ref('base_ecom__sales_orders') }}

),

ship_methods as (
    select * from {{ ref('ship_method') }}
),

renamed as (

    select
        b.sales_order_id,
        b.customer_id,
        b.account_number,
        b.bill_to_address_id,
        b.comment,
        b.credit_card_approval_code,
        b.credit_card_id,
        b.currency_rate_id,
        
        -- Handling the delivery days noise:
        CASE 
            WHEN b.delivery_estimate ILIKE '%week%' 
                THEN REGEXP_SUBSTR(b.delivery_estimate, '[0-9]+')::INT * 7
            WHEN b.delivery_estimate ILIKE '%day%' 
                THEN REGEXP_SUBSTR(b.delivery_estimate, '[0-9]+')::INT
            ELSE NULL  
        END     
            as delivery_estimate_days,

        b.due_date,
        b.freight,
        b.modified_date,
        b.online_order_flag,
        b.order_date,
        b.order_details,
        b.purchase_order_number,
        b.revision_number,
        b.sales_order_number,
        b.sales_person_id,
        b.ship_date,
        s.name as shipping_method,
        b.ship_to_address_id,
        b.status,
        b.sub_total,
        b.tax_amt,
        b.territory_id,
        b.total_due
    from base b
    left join ship_methods s
    on b.ship_method_id = s.ship_method_id

)

select * from renamed
