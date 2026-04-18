# Technical Decisions

> Key design decisions made across this project — what I chose, what I considered, and why.

---

## Decision 1: Watermark-Based Incremental Extraction vs. Full Table Scans

**Context:** The ETL processor needs to pull from PostgreSQL and MongoDB on a recurring schedule. I had to decide whether to pull every record every cycle or only new records since the last run.

**Decision:** Watermark-based incremental extraction using a `last_modified` timestamp filter stored in a metadata table.

**Alternatives considered:**
- **Full table scan each cycle:** Simpler — just SELECT * every time, no state to track. Rejected because as the tables grow, this burns compute pulling records I already have and will eventually become a bottleneck.
- **Change Data Capture (CDC) via PostgreSQL logical replication:** The most efficient option for high-volume changes. Rejected because it requires reconfiguring PostgreSQL at the server level and adds infrastructure complexity that is out of scope for this project.

**Trade-offs:**
- **Pros:** Only moves new data each cycle, keeps source system load low, the metadata table gives me an audit trail of what was pulled and when.
- **Cons:** Requires a reliable `last_modified` column on every source table. If a record is updated without that column changing, the watermark misses it.

**Rationale:** The source tables already have `last_modified` timestamps and the data volumes are in the thousands of records per cycle, not millions. Watermarks gave me efficiency without adding infrastructure. If this were a production pipeline at scale, CDC would be the right conversation to have with the DBA team.

---

## Decision 2: Snowflake as the Central Warehouse

**Context:** I needed a warehouse that could handle semi-structured JSON data from MongoDB, integrate natively with dbt, and not require me to manage infrastructure.

**Decision:** Snowflake with the VARIANT type for semi-structured data and native stages for loading.

**Alternatives considered:**
- **PostgreSQL (extend the existing source):** I already had PostgreSQL running as a source. Using it as the warehouse would eliminate one service. Rejected because it does not scale compute independently of storage, has no native VARIANT type for JSON, and mixing source and warehouse on the same database is a bad pattern.
- **BigQuery:** Strong alternative with similar compute/storage separation. Rejected because Snowflake had better native dbt support and the course infrastructure was already set up around it.

**Trade-offs:**
- **Pros:** Compute and storage scale independently — I can suspend the warehouse when not in use and pay nothing for idle time. VARIANT handles MongoDB's JSON without needing to pre-define a schema. Native dbt integration means I do not need extra connection setup.
- **Cons:** Snowflake has a learning curve around roles, warehouses, and account identifiers. The `show` tool in the dbt MCP server requires the warehouse to be running, so a suspended warehouse breaks live querying.

**Rationale:** For a pipeline that runs on a schedule rather than continuously, Snowflake's ability to suspend compute and pay nothing while idle is a significant cost advantage. The VARIANT type was also non-negotiable for handling MongoDB data cleanly without forcing a schema upfront.

---

## Decision 3: dbt for Transformation Instead of Raw SQL Scripts

**Context:** I needed to transform raw staged data through multiple layers — base parsing, staging cleanup, and intermediate joins. I had to choose between writing and running SQL scripts manually or using a transformation framework.

**Decision:** dbt with a Bronze → Silver → Gold medallion architecture, using models, tests, and documentation as first-class citizens.

**Alternatives considered:**
- **Raw SQL scripts run via Python:** Simpler setup, no new tool to learn. Rejected because there is no built-in lineage tracking, no test framework, and no documentation layer — you end up with a folder of SQL files that nobody can navigate.
- **Spark / PySpark:** Handles much larger data volumes and supports complex transformations. Rejected because the overhead of spinning up a Spark cluster is completely disproportionate to the data volumes here and would add significant infrastructure complexity.

**Trade-offs:**
- **Pros:** Native test framework (not_null, unique, relationships), auto-generated lineage graph, model documentation lives next to the code, dbt Cloud integration for CI/CD is straightforward.
- **Cons:** dbt adds a learning curve around the ref() system, materializations, and project structure. The Bronze/Silver/Gold layer distinction also requires discipline to maintain — it is easy to collapse layers if you are moving fast.

**Rationale:** The test framework alone was worth adopting dbt. Being able to write a `not_null` test and have it block a deploy in dbt Cloud if it fails is the difference between a pipeline that catches data problems and one that silently passes bad data to dashboards. The documentation requirement also pushed me to write agent-friendly descriptions that I would have skipped if the tooling did not surface them.

---

## Decision 4: Prefect for Orchestration vs. Airflow

**Context:** I needed something to schedule the ETL processor on a recurring interval and automatically retry if the run failed.

**Decision:** Prefect with a flow decorated with `@flow` and a deployment on a 15-minute schedule.

**Alternatives considered:**
- **Apache Airflow:** The industry standard for workflow orchestration. Rejected because Airflow requires a dedicated metadata database, a separate scheduler process, and significant configuration before you can write your first DAG. For a project at this scale, the setup cost is not worth it.
- **Cron jobs:** The simplest option — just a scheduled task. Rejected because cron gives you no retry logic, no visibility into run history, and no way to know if a job failed silently.

**Trade-offs:**
- **Pros:** Prefect's UI gives visibility into run history and failures. Retry logic is a decorator argument, not a manual implementation. The learning curve to get a first flow running is measured in minutes, not days.
- **Cons:** Prefect adds another service to manage (the Prefect server container). Airflow has more community plugins if I needed to integrate with additional systems in the future.

**Rationale:** The goal was reliable scheduling with automatic retries and enough observability to know when something broke. Prefect gave me all three without the Airflow setup overhead. For a team that is new to orchestration, Prefect's lower complexity means less time debugging infrastructure and more time building the pipeline.

---

## Decision 5: dbt MCP Server for Agent Access vs. a Custom REST API

**Context:** For Milestone 3, I needed to expose the warehouse data and model metadata to AI agents. I had to choose between building a custom REST API or using an existing MCP integration.

**Decision:** The dbt MCP server (`dbt-mcp`) running over SSE, exposing all 18 models with their documentation, lineage, and the ability to run queries via the `show` tool.

**Alternatives considered:**
- **Custom REST API wrapping Snowflake:** I could have built a FastAPI service that exposes specific endpoints for querying the warehouse. Rejected because a custom API has no awareness of model lineage, documentation, or the dbt DAG — the agent would only know what I explicitly built into the endpoints.
- **Snowflake-Native MCP:** Would allow the agent to run arbitrary SQL directly against the warehouse with full compute control. Rejected because it does not exist yet as a stable tool, and it would give the agent more direct access than I wanted without additional guardrails.

**Trade-offs:**
- **Pros:** The dbt MCP server is lineage-aware — the agent can trace which models feed which, explore documentation, and understand the full data graph without me building any of that. It also requires deep documentation to work well, which pushed me to write better model descriptions than I would have otherwise.
- **Cons:** The `show` tool (live querying) requires the Snowflake warehouse to be running. When the warehouse is suspended, the agent can still explore metadata but cannot execute queries. This is a meaningful limitation in a cost-conscious environment.

**Rationale:** For the use cases I care about — lineage exploration, model understanding, and natural language querying by non-technical users — the dbt MCP server covers all of them without requiring me to build and maintain a custom API. The documentation requirement was a net positive even though it added work, because it forced me to think about what an agent actually needs to reason about the data correctly.
