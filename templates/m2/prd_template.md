# Product Requirements Document: [Feature Name]

> This PRD is your specification for the AI agent. Write it BEFORE you start building with the agent. The better your spec, the better the agent's output. Think of this as the blueprint you'd hand to a junior developer.

---

## 1. Problem Statement

_What problem are we solving? Why does this matter for the Adventure Works data platform?_

[Write 2-3 sentences describing the business need. Example: "Adventure Works needs visibility into customer browsing behavior on its website. Currently, web analytics data exists in a REST API but is not integrated into the data warehouse, meaning analysts cannot connect browsing patterns to purchasing behavior."]

---

## 2. Desired Outcome

_What does "done" look like? Be specific._

[Describe the end state. What exists when this is complete? Example: "A Prefect flow that runs on a configurable schedule, pulls web analytics data from the API, cleans and validates it, loads it into Snowflake, and makes it available as a dbt source for downstream modeling."]

---

## 3. Acceptance Criteria

_How will we know this works? List specific, testable criteria._

- [ ] [Criterion 1, e.g., "Flow successfully connects to the API and retrieves data"]
- [ ] [Criterion 2, e.g., "Data is type-cast correctly (timestamps as TIMESTAMP, IDs as VARCHAR)"]
- [ ] [Criterion 3, e.g., "Null and duplicate records are handled gracefully"]
- [ ] [Criterion 4, e.g., "Data lands in Snowflake RAW_EXT.web_analytics_raw table"]
- [ ] [Criterion 5, e.g., "Flow handles API errors (timeouts, rate limits) with retries"]
- [ ] [Criterion 6, e.g., "Flow runs end-to-end without manual intervention"]

---

## 4. Technical Constraints

_What must the solution adhere to? These are non-negotiable._

- **Orchestration framework:** Prefect 2.0+
- **Target warehouse:** Snowflake (credentials via environment variables)
- **Loading pattern:** Upload to internal stage, then COPY INTO raw table
- **Containerization:** Must run in Docker, integrated with existing Docker Compose
- **Error handling:** Must include logging and graceful failure (no silent drops)
- **Scheduling:** Configurable interval via environment variable
- [Add any additional constraints specific to your implementation]

---

## 5. Data Schema

_What does the data look like? Document the expected fields._

### API Response Schema (Expected)

_Discover the API schema by exploring the documentation endpoints at your API base URL:_
- _`/docs` — Interactive Swagger UI_
- _`/agent-docs` — Agent-friendly markdown description_
- _`/example` — A single example event to inspect_

| Field | Type | Description | Nullable? |
|-------|------|-------------|-----------|
| [Document each field from the API response] | | | |

### Target Table Schema (Snowflake)

| Column | Type | Source |
|--------|------|--------|
| [Document the Snowflake table columns that will receive this data] | | |

---

## 6. Testing Requirements

_How should the agent test its work?_

- [ ] Unit test: Flow functions handle empty API response
- [ ] Unit test: Data cleaning handles null customer_id gracefully
- [ ] Unit test: Deduplication removes exact duplicates
- [ ] Integration test: Flow connects to API and retrieves at least one batch
- [ ] Integration test: Data lands in Snowflake raw table with correct types
- [ ] [Additional tests]

---

## 7. Out of Scope

_What should the agent NOT build? Set boundaries._

- [Example: "Do not build the dbt models for this data. That will be done separately."]
- [Example: "Do not modify existing dbt models or sources."]
- [Example: "Do not build a dashboard for this data."]

---

## 8. Questions and Assumptions

_What are you unsure about? What assumptions are you making?_

- **Assumption:** [Example: "The API returns paginated results with a `next_page` cursor"]
- **Assumption:** [Example: "The API rate limit is 100 requests per minute"]
- **Question:** [Example: "Should we store the raw JSON response or the parsed fields?"]
