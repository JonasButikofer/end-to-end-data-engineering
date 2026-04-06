with

orders as (

    select * from {{ source('real_time', 'orders_raw') }}

),

order_details as (

    select * from {{ source('real_time', 'order_details_raw') }}

),

order_details_aggregated as (

    select
        sales_order_id,
        array_agg(
            object_construct(
                'SalesOrderDetailID',       sales_order_detail_id,
                'CarrierTrackingNumber',     carrier_tracking_number,
                'OrderQty',                 order_qty,
                'ProductID',                product_id,
                'SpecialOfferID',           special_offer_id,
                'UnitPrice',                unit_price,
                'UnitPriceDiscount',        unit_price_discount,
                'LineTotal',                line_total,
                'ModifiedDate',             last_modified
            )
        ) as order_details
    from order_details
    group by sales_order_id

),

joined as (

    select
        o.sales_order_id,
        try_to_number(o.customer_id)            as customer_id,
        o.account_number,
        try_to_number(o.bill_to_address_id)     as bill_to_address_id,
        o.comment,
        o.credit_card_approval_code,
        try_to_number(o.credit_card_id)         as credit_card_id,
        try_to_number(o.currency_rate_id)       as currency_rate_id,
        o.due_date,
        o.freight,
        o.last_modified                         as modified_date,
        o.online_order_flag::integer            as online_order_flag,
        o.order_date,
        d.order_details,
        o.purchase_order_number,
        o.revision_number,
        o.sales_order_number,
        try_to_number(o.sales_person_id)        as sales_person_id,
        o.ship_date,
        try_to_number(o.ship_method_id)         as ship_method_id,
        try_to_number(o.ship_to_address_id)     as ship_to_address_id,
        o.status,
        o.sub_total,
        o.tax_amt,
        try_to_number(o.territory_id)           as territory_id,
        o.total_due
    from orders o
    left join order_details_aggregated d
        on o.sales_order_id = d.sales_order_id

)

select * from joined

