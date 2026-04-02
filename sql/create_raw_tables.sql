-- ============================================================================
-- Milestone 1: Create Raw Tables
-- ============================================================================
-- Run these statements in your Snowflake worksheet.
-- Make sure you've set your database, schema, and warehouse first:
--
  USE WAREHOUSE boa_wh;
  USE DATABASE boa_db;
  USE SCHEMA RAW_EXT;
--
-- The processor will automatically create the stages (orders_stage,
-- order_details_stage, chat_stage) when it runs, so you only need
-- to create the tables below.
-- ============================================================================

-- Orders from PostgreSQL (sales order headers)
CREATE TABLE IF NOT EXISTS orders_raw (
    sales_order_id VARCHAR,
    revision_number INT,
    status VARCHAR,
    online_order_flag BOOLEAN,
    sales_order_number VARCHAR,
    purchase_order_number VARCHAR,
    account_number VARCHAR,
    customer_id VARCHAR,
    sales_person_id VARCHAR,
    territory_id VARCHAR,
    bill_to_address_id VARCHAR,
    ship_to_address_id VARCHAR,
    ship_method_id VARCHAR,
    credit_card_id VARCHAR,
    credit_card_approval_code VARCHAR,
    currency_rate_id VARCHAR,
    sub_total DECIMAL(18, 2),
    tax_amt DECIMAL(18, 2),
    freight DECIMAL(18, 2),
    total_due DECIMAL(18, 2),
    comment VARCHAR,
    due_date TIMESTAMP,
    order_date TIMESTAMP,
    ship_date TIMESTAMP,
    last_modified TIMESTAMP
);

-- Order line items from PostgreSQL
CREATE TABLE IF NOT EXISTS order_details_raw (
    sales_order_detail_id VARCHAR,
    sales_order_id VARCHAR,
    carrier_tracking_number VARCHAR,
    order_qty INT,
    product_id VARCHAR,
    special_offer_id VARCHAR,
    unit_price DECIMAL(18, 2),
    unit_price_discount DECIMAL(18, 2),
    line_total DECIMAL(18, 2),
    last_modified TIMESTAMP
);

-- Chat logs from MongoDB (stored as semi-structured VARIANT)
CREATE TABLE IF NOT EXISTS chat_logs_raw (
    raw VARIANT
);
