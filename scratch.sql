USE DATABASE boa_db;
USE SCHEMA raw_ext;

LIST @orders_stage;
LIST @order_details_stage;
LIST @chat_stage;



select * from raw_ext.orders_raw order by order_date desc limit 5;
SELECT COUNT(*) FROM raw_ext.order_details_raw;
SELECT * FROM raw_ext.chat_logs_raw limit 5;


SHOW SCHEMAS IN DATABASE is566;

SHOW SCHEMAS IN DATABASE boa_db;



SELECT max(last_modified) FROM BOA_DB.RAW_EXT.orders_raw limit 5; 

SELECT
    country_region,
    SUM(total_due) AS total_sales,
    order_date
FROM BOA_DB.DBT_DEV.INT_SALES_ORDER_WITH_CUSTOMERS
Group by country_region, order_date;


select * from BOA_DB.DBT_DEV.INT_SALES_ORDER_WITH_CUSTOMERS limit 5;