# Technical Decisions

> Document 3-5 key design decisions you made across this project. For each decision, explain what you chose, what alternatives you considered, the trade-offs involved, and why you made the choice you did. This is the kind of document that demonstrates architectural thinking to a hiring manager.

---

## Decision 1: [Title, e.g., "Python-driven COPY INTO vs. Snowflake Tasks"]

**Context:** [What situation required a decision? 1-2 sentences.]

**Decision:** [What did you choose?]

**Alternatives considered:**
- [Alternative A]: [Brief description and why it was rejected]
- [Alternative B]: [Brief description and why it was rejected]

**Trade-offs:**
- **Pros of chosen approach:** [What you gain]
- **Cons of chosen approach:** [What you give up]

**Rationale:** [Why this was the right call for this project. 2-3 sentences.]

---

## Decision 2: [Title]

**Context:** [What situation required a decision?]

**Decision:** [What did you choose?]

**Alternatives considered:**
- [Alternative A]: [Description]
- [Alternative B]: [Description]

**Trade-offs:**
- **Pros:** [What you gain]
- **Cons:** [What you give up]

**Rationale:** [Why this was the right call.]

---

## Decision 3: [Title]

**Context:** [What situation required a decision?]

**Decision:** [What did you choose?]

**Alternatives considered:**
- [Alternative A]: [Description]
- [Alternative B]: [Description]

**Trade-offs:**
- **Pros:** [What you gain]
- **Cons:** [What you give up]

**Rationale:** [Why this was the right call.]

---

_Add Decisions 4 and 5 if applicable. Quality matters more than quantity. Three well-reasoned decisions are better than five shallow ones._

---

## Example (for reference, delete before submitting)

### Decision: Incremental extraction with watermarks vs. full table scans

**Context:** The ETL processor needs to extract data from PostgreSQL on a recurring schedule. We needed to decide whether to extract all records every cycle or only new/modified records.

**Decision:** Watermark-based incremental extraction using a `last_modified` timestamp filter.

**Alternatives considered:**
- **Full table scan each cycle:** Simpler to implement (just SELECT *), no metadata tracking needed. Rejected because it would grow linearly with table size and waste compute on unchanged records.
- **Change Data Capture (CDC) via PostgreSQL logical replication:** Most efficient for high-volume changes. Rejected because it requires PostgreSQL configuration changes and adds infrastructure complexity beyond project scope.

**Trade-offs:**
- **Pros:** Efficient (only processes new data), simple to implement (single WHERE clause), metadata tracking enables auditability
- **Cons:** Requires a reliable `last_modified` column on every source table, missed updates if timestamps are unreliable, watermark state must be persisted

**Rationale:** Watermark extraction balances efficiency with simplicity. The source tables already have `last_modified` columns, and the metadata table pattern is straightforward. For the data volumes in this project (hundreds of records per cycle), this is more than sufficient. In a production environment with millions of rows per cycle, we might reconsider CDC.
