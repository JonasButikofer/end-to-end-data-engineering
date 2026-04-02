USE DATABASE boa_db;
USE SCHEMA raw_ext;

LIST @orders_stage;
LIST @order_details_stage;
LIST @chat_stage;


SELECT COUNT(*) FROM raw_ext.orders_raw;
SELECT COUNT(*) FROM raw_ext.order_details_raw;
SELECT COUNT(*) FROM raw_ext.chat_logs_raw;