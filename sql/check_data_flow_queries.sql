-- ============================================================================
-- Milestone 1: Data Flow Validation Queries
-- ============================================================================
-- Run these queries one at a time to trace data through your pipeline.
-- Set your database first: USE DATABASE <your_database>;
-- ============================================================================


-- =============================================
-- CHECK 1: Do all raw tables have recent data?
-- =============================================
-- SUCCESS: All 3 tables have rows > 0, and the most recent dates
-- are within the last few days (from the generator).

SELECT
    'orders_raw' AS table_name,
    COUNT(*) AS row_count,
    MIN(order_date) AS earliest,
    MAX(order_date) AS latest
FROM raw_ext.orders_raw
UNION ALL
SELECT
    'order_details_raw',
    COUNT(*),
    MIN(last_modified),
    MAX(last_modified)
FROM raw_ext.order_details_raw
UNION ALL
SELECT
    'chat_logs_raw',
    COUNT(*),
    NULL,
    NULL
FROM raw_ext.chat_logs_raw;


-- =============================================
-- CHECK 2: Are all stages empty?
-- =============================================
-- SUCCESS: Each query returns 0 rows (no files remaining).
-- If files are present, the processor's cleanup step didn't run
-- or COPY INTO failed for that stage.

LIST @raw_ext.orders_stage;
LIST @raw_ext.order_details_stage;
LIST @raw_ext.chat_stage;


-- =============================================
-- CHECK 3: Do the dbt models exist with data?
-- =============================================
-- SUCCESS: All 4 models have rows > 0.
-- stg_ecom__sales_orders should have the most (legacy + new data).

SELECT 'stg_ecom__sales_orders' AS model, COUNT(*) AS rows FROM dbt_dev.stg_ecom__sales_orders
UNION ALL
SELECT 'stg_real_time__chat_logs', COUNT(*) FROM dbt_dev.stg_real_time__chat_logs
UNION ALL
SELECT 'int_sales_order_line_items', COUNT(*) FROM dbt_dev.int_sales_order_line_items
UNION ALL
SELECT 'int_sales_orders_with_campaign', COUNT(*) FROM dbt_dev.int_sales_orders_with_campaign;


-- =============================================
-- CHECK 4: Does stg_ecom__sales_orders have BOTH
--          legacy and recently generated data?
-- =============================================
-- SUCCESS: You see rows in both buckets. The "legacy" bucket is the
-- Adventure Works data from 2011-2014. The "recent" bucket is from
-- the generator running in Docker.

SELECT
    CASE
        WHEN order_date < '2020-01-01' THEN 'legacy (Adventure Works)'
        ELSE 'recent (generator)'
    END AS data_source,
    COUNT(*) AS order_count,
    MIN(order_date) AS earliest,
    MAX(order_date) AS latest
FROM dbt_dev.stg_ecom__sales_orders
GROUP BY 1
ORDER BY 1;


-- =============================================
-- CHECK 5: Do orders have nested order_details?
-- =============================================
-- SUCCESS: avg_details_per_order is > 1 for both data sources.
-- This confirms the ARRAY_AGG in the staging model is working.

SELECT
    CASE
        WHEN order_date < '2020-01-01' THEN 'legacy'
        ELSE 'recent'
    END AS data_source,
    COUNT(*) AS orders,
    AVG(ARRAY_SIZE(order_details)) AS avg_details_per_order,
    MIN(ARRAY_SIZE(order_details)) AS min_details,
    MAX(ARRAY_SIZE(order_details)) AS max_details
FROM dbt_dev.stg_ecom__sales_orders
WHERE order_details IS NOT NULL
GROUP BY 1;


-- =============================================
-- CHECK 6: Row count sanity across layers
-- =============================================
-- SUCCESS: raw orders >= staged orders (raw may have more if
-- multiple processor cycles ran). Line items should be roughly
-- 3-5x the order count. Chat logs should be a smaller number.

SELECT
    'raw_ext.orders_raw' AS layer, COUNT(*) AS rows FROM raw_ext.orders_raw
UNION ALL
SELECT 'raw_ext.order_details_raw', COUNT(*) FROM raw_ext.order_details_raw
UNION ALL
SELECT 'raw_ext.chat_logs_raw', COUNT(*) FROM raw_ext.chat_logs_raw
UNION ALL
SELECT 'dbt_dev.stg_ecom__sales_orders', COUNT(*) FROM dbt_dev.stg_ecom__sales_orders
UNION ALL
SELECT 'dbt_dev.int_sales_order_line_items', COUNT(*) FROM dbt_dev.int_sales_order_line_items
UNION ALL
SELECT 'dbt_dev.stg_real_time__chat_logs', COUNT(*) FROM dbt_dev.stg_real_time__chat_logs;
