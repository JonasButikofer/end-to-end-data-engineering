-- =============================================================================
-- Snowflake Objects for Web Analytics Pipeline (Milestone 2)
-- =============================================================================
-- Run these statements in your Snowflake worksheet BEFORE running the Prefect
-- flow. Make sure you are using the correct database and warehouse.
-- =============================================================================

-- 1. Create the internal stage for uploading web analytics CSV files
CREATE STAGE IF NOT EXISTS RAW_EXT.WEB_ANALYTICS_STAGE
    COMMENT = 'Stage for web analytics CSV files uploaded by the Prefect flow';

-- 2. Create the raw table that receives COPY INTO data
CREATE TABLE IF NOT EXISTS RAW_EXT.web_analytics_raw (
    customer_id       INT            NOT NULL,
    product_id        INT            NOT NULL,
    session_id        VARCHAR(255)   NOT NULL,
    page_url          VARCHAR(1000),
    event_type        VARCHAR(50),
    event_timestamp   TIMESTAMP_NTZ  NOT NULL,
    _loaded_at        TIMESTAMP_NTZ  DEFAULT CURRENT_TIMESTAMP(),
    _file_name        VARCHAR(255)
);
