# Interview Log

## Round 1: Scoping and Constraints
**Date:** 2026-03-25

**Q:** How many students are you expecting to grade across all sections for this final project?
**A:** 80-120 students.

**Q:** For the automated AI scoring, do you have (or plan to build) a reference solution repo that mirrors the full student repo structure, or is this more rubric-based evaluation without a side-by-side solution?
**A:** Full reference repo. Will have or build a complete working solution that mirrors the student repo structure.

**Q:** What's your target per-student budget for AI-based grading across all 3 milestones?
**A:** $0.50-$2.00/student. Moderate budget, can evaluate core deliverables with AI.

**Q:** Is the oral exam primarily a learning verification tool, a grading tool, or both?
**A:** Both equally. Oral exam contributes meaningfully to the grade AND serves as an understanding check.

---

## Round 2: Evaluation Architecture
**Date:** 2026-03-25

**Q:** Does the three-tier approach (deterministic checks, targeted AI on code files, AI on subjective artifacts) sound right?
**A:** Three tiers, yes. Deterministic checks + targeted AI on code + AI on written artifacts makes sense.

**Q:** Should automated grading happen after each milestone or as a single consolidated evaluation at the end?
**A:** End-only grading. One consolidated evaluation of the final repo after Milestone 3.

**Q:** For the oral exam, once at the end, per milestone, or mid-project?
**A:** Once at the end. Single oral exam covering the full project after Milestone 3.

**Q:** How to handle the AI-authorship concern when students are explicitly encouraged to use AI assistants?
**A:** Both explain and modify. Best signal combines explanation ability with ability to reason about changes. Students should be able to articulate what their code does AND reason about how they'd change or extend it.

---

## Round 3: Oral Exam Logistics and LLM Backend
**Date:** 2026-03-25

**Q:** For oral exam logistics with 80-120 students, self-service, proctored, or hybrid?
**A:** Self-service. Students do it on their own time within a window. Simpler logistics.

**Q:** For production LLM integration in the final-grader, which approach?
**A:** Still evaluating. Needs more info on what's involved before committing.

**Q:** Pushback on end-only grading creating a feedback gap. Students get no automated feedback until after the project is completely done.
**A:** Acceptable tradeoff. Students have office hours, TAs, and in-class support. The grading doesn't need to be the feedback loop.

---
