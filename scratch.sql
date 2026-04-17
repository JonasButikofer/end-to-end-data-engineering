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


SELECT * FROM BOA_DB.RAW_EXT.web_analytics_raw limit 10;


SHOW TABLES IN SCHEMA RAW_EXT;
SHOW STAGES IN SCHEMA RAW_EXT;



SELECT COUNT(*) FROM dbt_dev.stg_web_analytics;
select * from dbt_dev.int_sales_orders_with_campaigns limit 10;I


SELECT * FROM boa_db.dbt_dev.INT_SALES_ORDERS_WITH_CAMPAIGN LIMIT 10;

select * from boa_db.dbt_dev.stg_real_time__chat_logs limit 5;





SELECT DISTINCT ticket_status FROM dbt_dev.stg_real_time__chat_logs;
SELECT DISTINCT ticket_type   FROM dbt_dev.stg_real_time__chat_logs;
SELECT DISTINCT ticket_subject FROM dbt_dev.stg_real_time__chat_logs;
SELECT DISTINCT customer_segment FROM dbt_dev.stg_ecom__email_campaigns;
SELECT DISTINCT ad_strategy      FROM dbt_dev.stg_ecom__email_campaigns;