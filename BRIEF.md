# IS 566 Final Project Grading Strategy: Exploration Brief

## Core Concept

Design a grading system for a 3-milestone data engineering capstone (80-120 students) that uses two complementary evaluation modes, both applied once at the end of the project (after Milestone 3):

1. **Automated AI scoring** of student code and artifacts against a full reference solution repo, using a three-tier approach (deterministic checks, targeted AI on code, AI on subjective artifacts). Adapted from the sql_grader utility. Budget: $0.50-$2.00/student.

2. **Oral examination** via the final-grader web app, generating LLM-driven questions about students' own code that test both explanation ability and reasoning about modifications. Carries real grade weight and serves as authorship/understanding verification.

## Key Decisions Made

- **2026-03-25**: Class size is 80-120 students (multiple sections). Grading must scale.
- **2026-03-25**: Full reference solution repo will exist, enabling solution-comparison grading.
- **2026-03-25**: AI grading budget is $0.50-$2.00/student total across all milestones.
- **2026-03-25**: Oral exam is both a grading tool and a verification tool.
- **2026-03-25**: Three-tier automated evaluation: (1) deterministic/free checks, (2) targeted AI on code files, (3) AI on subjective written artifacts.
- **2026-03-25**: Grading happens once at the end (after Milestone 3), not per-milestone.
- **2026-03-25**: Oral exam happens once at the end, covering all 3 milestones.
- **2026-03-25**: The oral exam signal is "both explain and modify" -- can the student articulate what their code does AND reason about how they'd change or extend it?

## Open Questions

### Automated Scoring
- Which specific files go in each tier? (Need to map every deliverable to a tier)
- What's the right prompt design for multi-file repo comparison vs. single-file SQL comparison?
- How to handle architecture diagrams (images) in automated scoring?
- ~~Should scoring happen per-milestone or end-only?~~ RESOLVED: End-only.
- ~~What does the solution look like?~~ RESOLVED: Full reference repo.

### Oral Exam
- What's the status of production-ready LLM and transcription integrations in final-grader?
- How many questions per student? What's the time budget per oral exam?
- Which code areas are highest-signal for oral exam questions?
- What rubric dimensions map to this project?
- How to handle logistics of 80-120 oral exams (scheduling, proctoring, infrastructure)?

### Weighting and Integration
- What's the split between automated score and oral exam score?
- Should one serve as a check on the other (flag discrepancies)?
- One cumulative grade or separate component grades?

### Cost Model
- Need to estimate tokens per student for the Tier 2 and Tier 3 files
- Batch API feasibility within budget

## Domain Map

1. **Automated Scoring Strategy** - File triage across tiers, prompt design, cost modeling
2. **Oral Exam Design** - Question generation, rubric dimensions, session structure, logistics
3. **Grading Architecture** - How both modes combine, weighting, discrepancy handling
4. **Cost and Scale** - Token budgets, batch processing
5. **Rubric Design** - Dimensions per milestone, granularity
6. **Logistics and Operations** - Timeline, student communication, infrastructure

## Constraints & Boundaries

- Class size: 80-120 students across multiple sections
- Budget: $0.50-$2.00/student for AI-based automated grading
- Full reference solution repo available for comparison
- Existing infrastructure: sql_grader production-ready; final-grader v1 needs real LLM/transcription clients
- Timeline: Grading plan finalized before assignment distribution
- Each student has own GitHub repo and Snowflake account
- 3 milestones over 3 weeks, each building on the previous
- Grading and oral exam both happen once, at end of project
