[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/7Tkgt8hQ)
# Final Project

The always-up-to-date instructions for this assignment can be found [here](https://github.com/byu-is-566/is-566-11-final-project-instuctions). 

I'd recommend that you only access the instructions via the web so that you always have the latest copy.

Oh and **refresh often** so you don't miss updates.

---

## Milestone 2: Web Analytics Pipeline

### What Was Built

Milestone 2 added a third data source — a REST API serving clickstream events from the Adventure Works web storefront — and built a full ingestion-to-staging pipeline around it:

- A **Prefect flow** (`prefect/flows/web_analytics_flow.py`) that polls the API on a schedule, deduplicates events, uploads them to a Snowflake internal stage, and COPYs them into the raw table using a watermark-based incremental strategy
- **dbt staging and intermediate models** (`models-m2/`) that clean and enrich the raw clickstream data
- **Data quality checks** via dbt generic tests, custom SQL tests, and source freshness validation
- **dbt Cloud** configured with a scheduled production job and a CI/CD job that runs on every pull request

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                             │
│                                                                 │
│  PostgreSQL (ecom)   MongoDB (support)   REST API (web clicks)  │
└──────┬──────────────────────┬───────────────────┬──────────────┘
       │                      │                   │
       │  Milestone 1         │  Milestone 1      │  Milestone 2
       │  processor/          │  processor/       │  Prefect Flow
       ▼                      ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Snowflake (BOA_DB)                          │
│                                                                 │
│  RAW_EXT schema                                                 │
│  ├── orders_raw          ├── order_details_raw                  │
│  ├── chat_logs_raw       └── web_analytics_raw  ◄── NEW         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │  dbt (local dev + dbt Cloud)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     dbt_dev / dbt_prod                          │
│                                                                 │
│  Staging layer                                                  │
│  ├── stg_ecom__sales_orders    ├── stg_adventure_db__customers  │
│  ├── stg_real_time__chat_logs  └── stg_web_analytics  ◄── NEW  │
│                                                                 │
│  Intermediate layer                                             │
│  ├── int_sales_orders_with_campaign                             │
│  ├── int_sales_order_line_items                                 │
│  └── int_web_analytics_with_customers  ◄── NEW                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │  dbt Cloud (scheduled + CI/CD)
                               ▼
                     Snowsight Dashboards
```

### Data Sources

| Source | Type | Ingestion | Raw Table |
|--------|------|-----------|-----------|
| AdventureWorks ecom (PostgreSQL) | Transactional orders | Milestone 1 processor | `orders_raw`, `order_details_raw` |
| Support chat logs (MongoDB) | Unstructured chat | Milestone 1 processor | `chat_logs_raw` |
| Web analytics API (REST) | Clickstream events | Prefect flow (M2) | `web_analytics_raw` |

### Data Quality Strategy

- **Generic tests** on all staging models: `not_null`, `unique`, `accepted_values`, `relationships`
- **Source freshness** configured on `web_analytics_raw`: warns at 12h, errors at 24h — run with `dbt source freshness`
- **Custom SQL tests** in `dbt/tests/`:
  - `web_analytics_row_count_minimum.sql` — ensures at least 50 rows in staging
  - `web_analytics_freshness_check.sql` — verifies most recent event is within 4 hours
- All 46 tests pass as of Milestone 2 completion

### Agent Log

Development for Milestone 2 was done with Claude Code (claude-sonnet-4-6). See [`prefect/agent_log.md`](prefect/agent_log.md) for a full record of the AI-assisted development process, including 9 iteration rounds, errors encountered, and lessons learned. Key takeaways: the agent was strong on Snowflake-specific patterns and flow architecture, but required human verification for infrastructure state (database names, DDL pre-reqs).

### Setup — New in Milestone 2

**New environment variables** (add to your `.env.dev`):

```bash
API_BASE_URL=https://is566-web-analytics-api.fly.dev
PREFECT_API_URL=http://prefect-server:4200/api
FLOW_SCHEDULE_MINUTES=15
```

**Start Prefect services:**

```bash
docker compose up -d prefect-server prefect-worker web-analytics-flow
```

**Run the web analytics flow manually:**

```bash
cd prefect
.venv\Scripts\python.exe -m flows.web_analytics_flow
```

**Run dbt models for Milestone 2 only:**

```bash
cd dbt
dbt build --select models-m2
```

**Check source freshness:**

```bash
dbt source freshness
```