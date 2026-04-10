# Agent Interaction Log: M2 Web Analytics Prefect Flow & dbt Integration

> Document your experience building this feature with an AI agent. This log is a learning artifact, not a test. Be honest about what worked and what didn't.

---

## 1. Setup

**Agent tool used:** Claude Code (claude-sonnet-4-6) via VS Code extension

**Why this tool?** Claude Code has strong context awareness of the full project file tree and can read, write, and run terminal commands in one session without switching between tools. It also handles multi-file refactors well, which was needed for the dbt model hierarchy.

**Date:** April 2026

**Total time spent:** Approximately 4-5 hours across multiple sessions

---

## 2. Initial Specification

_What did you give the agent to start with?_

```
I am making this PRD for the next part of the implementation in m2.
Is this doc ready to implement or are there more things that it is missing?
```

I shared a stream-of-thought PRD.txt describing the web analytics Prefect flow. The agent identified missing details (exact file path, table schema with column name clarifications, watermark strategy, dedup key, full dependency list) and consolidated everything into a structured `prefect/prd.md`.

**Did you share the PRD with the agent?** Yes — I pasted the raw PRD text into the chat. The agent read it, identified gaps, and produced the final version.

---

## 3. Iteration Log

### Iteration 1: PRD review and structuring
- **What I asked:** Whether the PRD was ready to implement and if anything was missing
- **What the agent produced:** A gap analysis listing missing fields: exact output file path, table DDL with correct column names, watermark query pattern, dedup key definition, and Python dependency list
- **What worked:** The agent caught that the raw PRD used `timestamp` but Snowflake best practice is `event_timestamp` (avoids reserved word conflicts), and that the dedup strategy wasn't specified
- **What didn't work:** Nothing significant at this stage
- **What I changed:** Asked the agent to write the full PRD.md incorporating all gaps

### Iteration 2: Prefect flow implementation
- **What I asked:** Implement the PRD — build `prefect/flows/web_analytics_flow.py`
- **What the agent produced:** A 6-task Prefect flow: `get_watermark`, `fetch_events`, `clean_and_validate`, `upload_to_stage`, `copy_into_raw`, `clean_stage`. Each task had try/except blocks and record count logging. Watermark sourced from `MAX(event_timestamp)` in Snowflake. Exponential backoff on HTTP 429s. Dedup on `(session_id, event_type, event_timestamp)`. Stage cleanup skipped if COPY INTO failed.
- **What worked:** The overall flow structure and task decomposition were correct on the first pass. Error handling patterns (retry on 429, skip cleanup on failure) matched the PRD intent.
- **What didn't work:** The flow couldn't connect to Snowflake on first run — account returned as `None`.
- **What I changed:** Diagnosed the env loading issue (see Iteration 3)

### Iteration 3: Snowflake account `None` — env loading path fix
- **What I asked:** Why is `SNOWFLAKE_ACCOUNT` resolving to `None`?
- **What the agent produced:** Diagnosis: `load_dotenv()` was called without a path, so it searched from `prefect/flows/` and never found `.env.dev` which lives at the project root (three levels up). Fix: construct an explicit path using `os.path.dirname(__file__)` navigating three directories up.
- **What worked:** The path fix resolved the issue immediately
- **What didn't work:** Nothing after this fix
- **What I changed:** Applied the `_root = os.path.abspath(...)` pattern the agent wrote

### Iteration 4: Snowflake stage does not exist
- **What I asked:** Flow ran but threw `WEB_ANALYTICS_STAGE does not exist`
- **What the agent produced:** Explanation that the stage DDL in `prefect/snowflake_objects.sql` had to be run manually in a Snowflake worksheet before the flow could PUT files. The flow assumes the stage already exists — it doesn't create it.
- **What worked:** Ran the DDL, stage created, next flow run succeeded
- **What didn't work:** N/A
- **What I changed:** Ran `prefect/snowflake_objects.sql` in the Snowflake UI

### Iteration 5: Docker container name conflicts and port collision
- **What I asked:** `docker compose up` failing with port 4200 already allocated and container name conflicts
- **What the agent produced:** Identified that old stopped containers (`prefect-server`, `prefect-worker`) from a previous session were still registered in Docker's namespace, blocking new containers from using the same names. Fix: `docker rm prefect-server && docker rm prefect-worker`, then re-run compose.
- **What worked:** Removing the old containers resolved both the name conflict and the port conflict
- **What didn't work:** N/A
- **What I changed:** Added `docker compose down` to my workflow before each session

### Iteration 6: dbt models-m2 setup and sources.yml
- **What I asked:** How to define the source for web_analytics_raw with all column descriptions and tests per section 3.2 of the instructions
- **What the agent produced:** Full `sources.yml` with `database: boa_db`, schema `RAW_EXT`, freshness config (warn 12h, error 24h), and column-level tests including `not_null`, `accepted_values` on event_type, and a `relationships` test linking customer_id to `stg_adventure_db__customers`.
- **What worked:** Column definitions and freshness config were correct
- **What didn't work:** Two errors: (1) database was initially `is566` instead of `boa_db` — caught after `SHOW SCHEMAS IN DATABASE is566` returned nothing; (2) `accepted_values` used the old flat syntax instead of the dbt 1.11 `arguments:` nesting
- **What I changed:** Updated database to `boa_db` after confirming in Snowflake UI; updated accepted_values YAML to use `arguments: values: [...]` syntax

### Iteration 7: stg_web_analytics model and type errors
- **What I asked:** Write the staging model and its companion YAML
- **What the agent produced:** `stg_web_analytics.sql` casting `_loaded_at` to `timestamp_ntz`, renaming it to `loaded_at`, and adding `current_timestamp()` as `dbt_loaded_at`
- **What worked:** The model logic and column renames were correct
- **What didn't work:** Initial cast used `timestamp_utc` which is not a valid Snowflake type; also a missing comma in the CTE syntax
- **What I changed:** Agent fixed both: changed to `timestamp_ntz`, added the missing comma after the source CTE closing paren

### Iteration 8: int_web_analytics_with_customers — customer_id type mismatch
- **What I asked:** Write the intermediate model enriching clickstream with customer geography
- **What the agent produced:** A left join on `cs.customer_id = c.customer_id` with all customer geography columns
- **What worked:** Column selection and join logic were correct
- **What didn't work:** Join returned no matches because `stg_web_analytics.customer_id` is INTEGER and `stg_adventure_db__customers.customer_id` is VARCHAR — Snowflake doesn't implicit-cast on join
- **What I changed:** Agent added `cs.customer_id::string = c.customer_id` explicit cast

### Iteration 9: Snowflake resource monitor quota exceeded
- **What I asked:** dbt build returned 16 errors — all timeout/warehouse suspended errors
- **What the agent produced:** Diagnosis: BOA_MONITOR quota was exhausted (Prefect flow running every 15 min + data generator running every minute). Recommendation: `docker compose down`, stop the generator, contact professor to reset BOA_MONITOR.
- **What worked:** Stopping all services immediately halted credit burn
- **What didn't work:** N/A — this was an infrastructure limit, not a code error
- **What I changed:** Shut everything down and emailed professor

---

## 4. Final Result

**Did the agent-generated code work on first run?** No

**If no, what broke?**
- Snowflake connection returned `None` for account (env loading path)
- Stage didn't exist (DDL needed to be run manually first)
- Docker container name and port conflicts from a prior session
- `timestamp_utc` is not a valid Snowflake type (should be `timestamp_ntz`)
- `accepted_values` YAML syntax was outdated for dbt 1.11
- Customer ID type mismatch on the intermediate model join

**Percentage of final code written by the agent vs. you:**
- Agent wrote: ~85%
- I wrote/modified: ~15% (running DDL manually, confirming database names in Snowflake UI, minor YAML fixes)

**Key files the agent created or modified:**
- [prefect/prd.md](prefect/prd.md): Structured PRD consolidated from stream-of-thought notes, with gap analysis additions
- [prefect/flows/web_analytics_flow.py](prefect/flows/web_analytics_flow.py): Full 6-task Prefect flow with watermark, dedup, staging, COPY INTO, and cleanup
- [dbt/models-m2/staging/web_analytics/sources.yml](dbt/models-m2/staging/web_analytics/sources.yml): Source definition with freshness config and column tests
- [dbt/models-m2/staging/web_analytics/stg_web_analytics.sql](dbt/models-m2/staging/web_analytics/stg_web_analytics.sql): Staging model with type casts and metadata column
- [dbt/models-m2/staging/web_analytics/stg_web_analytics.yml](dbt/models-m2/staging/web_analytics/stg_web_analytics.yml): Companion YAML with data tests
- [dbt/models-m2/staging/web_analytics/intermediate/int_web_analytics_with_customers.sql](dbt/models-m2/staging/web_analytics/intermediate/int_web_analytics_with_customers.sql): Intermediate model joining clickstream to customer geography
- [dbt/dbt_project.yml](dbt/dbt_project.yml): Added `models-m2` to model-paths
- [compose.yml](compose.yml): Uncommented Prefect services and web-analytics-flow

---

## 5. What I Learned

### What the agent was good at:
- Generating the full Prefect flow structure quickly from a PRD — the 6-task decomposition (watermark → fetch → clean → stage → copy → cleanup) was correct on the first pass
- Writing error handling patterns: exponential backoff on 429, skipping stage cleanup when COPY INTO fails to preserve files for retry
- Reading existing project files to match naming conventions and avoid conflicts with M1 models
- Diagnosing errors from stack traces — the `None` account issue and the type mismatch on the join were identified immediately from the error output
- Knowing Snowflake-specific syntax (ARRAY_AGG+OBJECT_CONSTRUCT, TRY_TO_NUMBER, COPY INTO, internal stages)

### What the agent struggled with:
- Getting the `.env` loading path right without being told the file was at project root — assumed relative to cwd rather than checking all ancestor directories
- Keeping up with dbt version-specific YAML syntax changes (`accepted_values` arguments nesting changed in 1.11)
- Knowing the correct Snowflake database name (`boa_db` vs `is566`) without access to the Snowflake account — required manual verification

### What I would do differently next time:
- Share the `.env.dev` path explicitly in the initial prompt so the agent doesn't need to guess
- Run `SHOW DATABASES` and paste the output before asking the agent to write any sources.yml — eliminates the wrong-database iteration entirely
- Run the Snowflake DDL files before starting the Prefect flow, not after the first failure

### Time comparison estimate:
- **With agent:** ~4-5 hours
- **Without agent (estimate):** ~12-15 hours (researching Prefect 2.0 PUT/COPY INTO patterns, Snowflake stage setup, dbt incremental configs, watermark logic from scratch)
- **Net impact:** ~3x faster. The biggest savings were in the Snowflake-specific patterns (stage management, COPY INTO syntax) and the dbt test YAML structure, which would have required significant documentation reading.

---

## 6. Reflection

Using Claude Code for this milestone felt less like pair programming and more like having a senior engineer who had read all the documentation but hadn't touched this specific codebase before. It produced correct architectural decisions — watermark-based incremental extraction, skipping stage cleanup on COPY INTO failure, dedup before staging — without being prompted for those details. The failures were almost entirely environmental: wrong database name, missing DDL, path resolution. None of the logic errors required more than one correction round. The most surprising part was how well it handled Snowflake-specific quirks like `TRY_TO_NUMBER` for NaN strings and `::string` casts on join keys — patterns that aren't in generic SQL tutorials but are real production gotchas. My main concern going forward is that the agent can't verify infrastructure state (does the stage exist? what's the real database name?) without me supplying that context, which means the human-in-the-loop role shifts from writing code to verifying preconditions. That's a different skill than traditional development, but arguably a more valuable one.
