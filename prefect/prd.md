# Product Requirements Document: Web Analytics Prefect Flow

---

## 1. Problem Statement

Adventure Works currently has sales, order, and customer support data flowing through the warehouse, but has no visibility into what customers are doing on the website before they buy. Web analytics data (page views, clicks, add-to-cart events, purchases) exists in a REST API but is not yet integrated into the data warehouse. This means analysts cannot connect browsing behavior to purchasing patterns.

This flow will close that gap by pulling clickstream events from the API on a recurring schedule and landing them in Snowflake, where they can be joined with existing customer and sales data.

---

## 2. Desired Outcome

A Prefect 2.0 flow running inside the existing Docker Compose environment that:

1. Pulls new clickstream events from the web analytics REST API using the `since` parameter for incremental extraction
2. Cleans, validates, and deduplicates the data
3. Stages it in a Snowflake internal stage
4. Loads it into `RAW_EXT.web_analytics_raw` using COPY INTO
5. Cleans up staged files after a successful load
6. Logs summary statistics for each run

---

## 3. Acceptance Criteria

- [ ] Flow connects to the API and retrieves clickstream events
- [ ] Flow uses the `since` parameter so only new events are fetched each run
- [ ] Watermark is derived from `MAX(event_timestamp)` in `RAW_EXT.web_analytics_raw` at the start of each run (not from a local file or system clock)
- [ ] Data is type-cast correctly: `customer_id` and `product_id` as INT, `session_id`/`page_url`/`event_type` as VARCHAR, `timestamp` as TIMESTAMP_NTZ
- [ ] Records are deduplicated on `(session_id, event_type, event_timestamp)` before loading
- [ ] Flow handles 429 rate limiting with exponential backoff and retries
- [ ] Flow handles HTTP errors and timeouts gracefully — no silent data drops
- [ ] Data lands in `RAW_EXT.web_analytics_raw` with correct column mapping (note: API field `timestamp` maps to table column `event_timestamp`)
- [ ] Staged files are cleaned from `@RAW_EXT.WEB_ANALYTICS_STAGE` after successful COPY INTO
- [ ] If COPY INTO fails, staged files are NOT removed (left for retry)
- [ ] Summary statistics are logged each run: records fetched, records after deduplication, records loaded
- [ ] Flow runs on a configurable schedule via `FLOW_SCHEDULE_MINUTES` environment variable
- [ ] Flow is deployable via the existing Docker Compose setup

---

## 4. Technical Constraints

- **Orchestration:** Prefect 2.0+ (already in `pyproject.toml`)
- **File to implement:** `prefect/flows/web_analytics_flow.py` (currently empty — write the full implementation here)
- **Target warehouse:** Snowflake — credentials via environment variables from `.env`
- **Stage:** `@RAW_EXT.WEB_ANALYTICS_STAGE`
- **Raw table:** `RAW_EXT.web_analytics_raw`
- **Loading pattern:** Upload CSV to internal stage → COPY INTO raw table → REMOVE staged files
- **Containerization:** Must run inside the existing Docker Compose environment
- **Dependencies:** Use only what is already in `pyproject.toml` — do NOT add new packages:
  - `prefect>=2.14,<3.0`
  - `snowflake-connector-python>=3.5`
  - `requests>=2.31`
  - `pandas>=2.1`
  - `python-dotenv>=1.0`
- **Environment variables** (all loaded from `.env`):
  - `API_BASE_URL=https://is566-web-analytics-api.fly.dev`
  - `FLOW_SCHEDULE_MINUTES` — interval between flow runs
  - `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_SCHEMA`

---

## 5. Data Schema

### API Endpoint

```
GET {API_BASE_URL}/analytics/clickstream?since=<ISO8601 timestamp>
```

Returns a JSON array of event objects. Defaults to the last 60 minutes if `since` is omitted (~50 events/hour).

### API Response Schema

| Field | Type | Description | Nullable? |
|-------|------|-------------|-----------|
| `customer_id` | Integer (11,000–30,118) | Joins with `stg_adventure_db__customers` | No |
| `product_id` | Integer (707–999) | Joins with `stg_adventure_db__products` | No |
| `session_id` | String (`sess_` + 12 hex chars) | Unique per browsing session | No |
| `page_url` | String | URL of the page visited | No |
| `event_type` | Enum: `page_view`, `click`, `add_to_cart`, `purchase` | Funnel stage | No |
| `timestamp` | ISO 8601 UTC | Event time — use as watermark for incremental pulls | No |

### Event Funnel Distribution

- `page_view` — 50%
- `click` — 25%
- `add_to_cart` — 15%
- `purchase` — 10%
- Sessions contain 1–8 events; one customer may have multiple sessions

### Target Table Schema (`RAW_EXT.web_analytics_raw`)

The table and stage already exist in Snowflake (created via `prefect/snowflake_objects.sql`).

| Column | Type | Source |
|--------|------|--------|
| `customer_id` | INT NOT NULL | API `customer_id` |
| `product_id` | INT NOT NULL | API `product_id` |
| `session_id` | VARCHAR(255) NOT NULL | API `session_id` |
| `page_url` | VARCHAR(1000) | API `page_url` |
| `event_type` | VARCHAR(50) | API `event_type` |
| `event_timestamp` | TIMESTAMP_NTZ NOT NULL | API `timestamp` (rename on load) |
| `_loaded_at` | TIMESTAMP_NTZ | Auto-populated by Snowflake default |
| `_file_name` | VARCHAR(255) | Populated by COPY INTO metadata |

---

## 6. Existing Warehouse Context

The flow only needs to load into the raw table. The following dbt models already exist and will join with the web analytics data downstream — the flow does not need to touch them:

- `stg_adventure_db__customers` — customer dimension with `customer_id`, `country_region`, `city`
- `stg_adventure_db__products` — product dimension with `product_id`
- `int_sales_order_line_items` — flattened order line items with `customer_id`, `product_id`, `order_date`
- `int_sales_orders_with_campaign` — orders joined with email campaign conversions
- `int_sales_order_with_customers` — orders with customer geography (last 30 days)
- `stg_real_time__chat_logs` — customer support chat logs with `customer_id`, `product_id`

---

## 7. Testing Requirements

- [ ] Flow imports cleanly: `python -c "from flows.web_analytics_flow import web_analytics_flow; print('OK')"`
- [ ] Local run succeeds: `uv run python -m flows.web_analytics_flow`
- [ ] Empty API response is handled gracefully (no crash, logs 0 records fetched)
- [ ] Null `customer_id` or `product_id` records are dropped before loading
- [ ] Deduplication removes exact duplicates on `(session_id, event_type, event_timestamp)`
- [ ] Data appears in `RAW_EXT.web_analytics_raw` after a successful run
- [ ] Stage is empty after successful load
- [ ] Flow runs on schedule inside Docker Compose

---

## 8. Out of Scope

- dbt models for web analytics data (handled separately in Task 3)
- Modifications to any existing M1 dbt models or sources
- Dashboard changes
- Any new Python dependencies not already in `pyproject.toml`

---

## 9. Assumptions

- The watermark is derived from `MAX(event_timestamp)` in `RAW_EXT.web_analytics_raw` at flow start. On the first run (empty table), fetch the last 60 minutes of data (omit `since`).
- Deduplication key is `(session_id, event_type, event_timestamp)` — applied in pandas before staging.
- One session may contain 1–8 events across multiple event types.
- A single customer may have multiple sessions.
- The API returns a flat JSON array (not paginated).
- Snowflake uses PAT authentication — `SNOWFLAKE_ROLE` is required.
