with

source as (

    select * from {{ source('adventure_db', 'customer_prod_db') }}

),

renamed as (

    select
        customerid::string         as customer_id,
        firstname                  as first_name,
        middlename                 as middle_name,
        lastname                   as last_name,
        fullname                   as full_name,
        emailaddress               as email_address,
        addressline1               as address_line_1,
        addressline2               as address_line_2,
        city                       as city,
        stateprovince              as state_province,
        countryregion              as country_region,
        postalcode                 as postal_code,
        accountnumber              as account_number,
        territoryid::string        as territory_id,
        modifieddate               as modified_date
    from source

)

select * from renamed