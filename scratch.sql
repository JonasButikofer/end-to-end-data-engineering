USE DATABASE boa_db;
USE SCHEMA raw_ext;

LIST @orders_stage;
LIST @order_details_stage;
LIST @chat_stage;


SELECT * FROM raw_ext.orders_raw limit 5;
SELECT COUNT(*) FROM raw_ext.order_details_raw;
SELECT * FROM raw_ext.chat_logs_raw limit 5;


SHOW SCHEMAS IN DATABASE is566;

SHOW SCHEMAS IN DATABASE boa_db;

