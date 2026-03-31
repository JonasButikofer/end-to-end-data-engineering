with

source as (

    select * from {{ source('adventure_db', 'inventory_prod_db') }}

),

renamed as (

    select
        productid::string   as product_id,
        locationid          as location_id,
        shelf               as shelf,
        bin                 as bin,
        quantity            as quantity
    from source

)

select * from renamed