with

source as (

    select * from {{ source('ecom_source', 'sales_order_raw') }}

),

renamed as (

    select
        raw:SalesOrderID::string            as sales_order_id,
        raw:CustomerID::string              as customer_id,
        raw:AccountNumber::string           as account_number,
        raw:BillToAddressID::number         as bill_to_address_id,
        raw:Comment::string                 as comment,
        raw:CreditCardApprovalCode::string  as credit_card_approval_code,
        raw:CreditCardID::number            as credit_card_id,
        raw:CurrencyRateID::number          as currency_rate_id,
        raw:DeliveryEstimate::string        as delivery_estimate,
        raw:DueDate::timestamp              as due_date,
        raw:Freight::float                  as freight,
        raw:ModifiedDate::date              as modified_date,
        raw:OnlineOrderFlag::integer        as online_order_flag,
        raw:OrderDate::timestamp            as order_date,
        raw:OrderDetails::variant           as order_details,
        raw:PurchaseOrderNumber::string     as purchase_order_number,
        raw:RevisionNumber::number          as revision_number,
        raw:SalesOrderNumber::string        as sales_order_number,
        raw:SalesPersonID::number           as sales_person_id,
        raw:ShipDate::timestamp             as ship_date,
        raw:ShipMethodID::number            as ship_method_id,
        raw:ShipToAddressID::number         as ship_to_address_id,
        raw:Status::number                  as status,
        raw:SubTotal::float                 as sub_total,
        raw:TaxAmt::float                   as tax_amt,
        raw:TerritoryID::number             as territory_id,
        raw:TotalDue::float                 as total_due
    from source

)

select * from renamed
