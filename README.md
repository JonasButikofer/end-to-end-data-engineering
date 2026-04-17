# Adventure Works Data Platform

> This project builds a production ready data pipeline on Snowflake and dbt that ingests Adventure Works sales, e-commerce, and real-time order data into a single warehouse, enabling reporting and agent accessible analytics via MCP.



## Architecture

<!-- 
  Replace this section with your architecture diagram. Options:
  1. Embed a Mermaid diagram (GitHub renders it natively) — see the example below
  2. Include an image: ![Architecture](screenshots/architecture.png)
  
  Your diagram should show:
  - All data sources (PostgreSQL, MongoDB, REST API)
  - Extract & ingest layer (ETL processor, Snowflake stages)
  - Orchestration (Prefect)
  - Raw layer
  - Transformation layers (dbt staging, intermediate)
  - Quality & CI/CD (dbt tests, dbt Cloud)
  - Analytics & access (dashboards, MCP server)
-->

**Caption:** [TODO: Write a 1-2 sentence caption explaining the end-to-end flow shown in the diagram.]

---

## Problem Statement

[TODO: Describe the business problem this platform solves. What data is spread across which systems? What questions can't stakeholders answer today? How does your platform address this? Aim for 3-5 sentences.]

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Source Systems | PostgreSQL, MongoDB, REST API | [TODO: Why do these represent real-world diversity?] |
| Extraction | Python ETL Processor | [TODO: Why a custom processor? What patterns does it use (e.g., watermarks)?] |
| Warehouse | Snowflake | [TODO: Why Snowflake specifically? Think about compute/storage separation, semi-structured data support, etc.] |
| Transformation | dbt | [TODO: Why dbt? Think about testing, documentation, lineage, version control.] |
| Orchestration | Prefect | [TODO: Why Prefect over alternatives? Think about retries, logging, simplicity.] |
| CI/CD | dbt Cloud + GitHub | [TODO: What does this give you? Automated builds, scheduled runs, etc.] |
| Agent Access | dbt MCP Server | [TODO: What does MCP enable? How does it expose your models to AI agents?] |
| Containerization | Docker Compose | [TODO: Why Docker? Think about reproducibility.] |

---

## Data Flow

[TODO: Describe the end-to-end data flow in 2-3 paragraphs. Cover:

**Paragraph 1 — Ingestion:** How does data enter the platform from each source? What extraction strategy do you use (watermarks, full refresh)? How is data staged and loaded into Snowflake?

**Paragraph 2 — Transformation:** What happens in the dbt layers? What do staging models do (cleaning, casting, renaming)? What do intermediate models do (joining across sources)? Give specific model names.

**Paragraph 3 — Serving:** How is the final data consumed? Dashboards? MCP server? How does testing and CI/CD fit in?]

---

## Setup and Run

### Prerequisites
- Docker Desktop
- Snowflake account (trial works)
- Python 3.9+
- dbt Cloud account (free tier)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/[TODO: your-username]/[TODO: your-repo-name].git
cd [TODO: your-repo-name]

# 2. Configure environment
cp .env.sample .env
# Edit .env with your Snowflake credentials

# 3. Create raw tables in Snowflake
# [TODO: describe how to set up the raw tables]

# 4. Start all services
docker compose up -d

# 5. Run dbt models and tests
cd dbt
dbt build

# 6. Start the MCP server
# [TODO: your MCP server start command]

# 7. (Optional) Run the MCP demo
cd mcp
uv sync
uv run python demo_client.py
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SNOWFLAKE_ACCOUNT` | Full Snowflake account identifier (e.g., `ab12345.us-east-1`) |
| `SNOWFLAKE_USER` | Snowflake username |
| `SNOWFLAKE_PASSWORD` | Snowflake password |
| `SNOWFLAKE_WAREHOUSE` | Compute warehouse name (e.g., `COMPUTE_WH`) |
| `SNOWFLAKE_DATABASE` | Target database (e.g., `IS566`) |
| `SNOWFLAKE_ROLE` | Snowflake role (default: `ACCOUNTADMIN`) |

See `.env.sample` for the full list.

---

## Project Milestones

### Milestone 1: Core Pipeline
[TODO: Summarize what you built in Milestone 1. Cover: ETL extraction sources, staging models created, intermediate models created, data quality tests implemented. Be specific — name your models and mention counts.]

### Milestone 2: Orchestration, Quality, and Agent-Assisted Development
[TODO: Summarize what you added in Milestone 2. Cover: Prefect orchestration, dbt Cloud integration, new models (web analytics), source freshness, dashboards.]

### Milestone 3: Agent Access and Portfolio
[TODO: Summarize what you completed in Milestone 3. Cover: MCP server deployment, documentation upgrades, demo client, portfolio finalization.]

---

## Key Metrics

<!-- Run actual Snowflake queries to fill in these numbers. Do NOT estimate or guess. -->

| Metric | Value |
|--------|-------|
| Raw records processed per cycle | [TODO: query your raw tables] |
| Pipeline execution time | [TODO: time your Docker Compose run] |
| dbt models | [TODO: run `dbt ls --resource-type model \| wc -l`] |
| dbt tests | [TODO: run `dbt ls --resource-type test \| wc -l`] |
| Test pass rate | [TODO: run `dbt test` and report pass/fail] |
| Data sources integrated | [TODO: count from sources.yml] |
| Source tables | [TODO: count] |
| Models exposed via MCP | [TODO: count from demo script output] |
| Source freshness SLA | [TODO: your freshness threshold] |

---

## What I Learned

[TODO: Write 4-6 sentences of genuine reflection. What surprised you? What was harder than expected? What would you do differently if starting over? What did you learn about data engineering as a discipline — not just the tools, but the craft? Avoid generic platitudes; be specific to YOUR experience.]

---

## Future Improvements

- **[TODO: Improvement 1 title]**: [TODO: Describe a specific improvement you'd make. Why would it matter? What problem would it solve?]
- **[TODO: Improvement 2 title]**: [TODO: Describe another improvement.]
- **[TODO: Improvement 3 title]**: [TODO: Describe another improvement.]

---

## Technical Decisions

See [technical_decisions.md](technical_decisions.md) for detailed documentation of key architectural choices.
