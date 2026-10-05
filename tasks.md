# tasks.md — AI Placement Mentor: Task Breakdown

Defines the concrete units of work. No implementation code here. See `claude.md` for principles, `spec.md` for requirements (referenced by FR/BR IDs below), `plan.md` for architecture/strategy this breakdown follows.

Each task lists: ID, description, objective, dependencies, priority (P0=blocking/critical path, P1=important, P2=nice-if-time), complexity (S/M/L), acceptance criteria, related module/spec IDs.

---

## Phase 0 — Discovery / Foundation

**0.1 — Confirm and freeze MVP scope**
Objective: ensure claude.md/spec.md/plan.md are the single source of truth before any building starts.
Dependencies: none. Priority: P0. Complexity: S.
Acceptance: all three documents committed to repo root; no open scope questions remain unresolved.

**0.2 — Set up repository structure**
Objective: create the modular-monolith backend skeleton (per plan.md Section 3 module boundaries) and frontend skeleton.
Dependencies: 0.1. Priority: P0. Complexity: S.
Acceptance: repo has clearly separated backend module folders matching plan.md's 13 modules, plus a frontend app skeleton; README points to the four planning docs.

---

## Phase 1 — Project Setup

**1.1 — Backend project scaffolding (FastAPI)**
Objective: initialize FastAPI project, dependency management, config/env-variable loading, base app structure.
Dependencies: 0.2. Priority: P0. Complexity: S.

**1.2 — Frontend project scaffolding (React)**
Objective: initialize React app, routing, base layout, API client setup.
Dependencies: 0.2. Priority: P0. Complexity: S.

**1.3 — Local development environment (Docker Compose)**
Objective: Postgres + backend + frontend runnable locally via one command, matching plan.md's containerization intent.
Dependencies: 1.1, 1.2. Priority: P0. Complexity: M.

---

## Phase 2 — Database

**2.1 — Core schema: users, student_profiles, education**
Dependencies: 1.3. Priority: P0. Complexity: M. Related: spec.md FR-5, FR-6, Section 10.
Acceptance: provenance fields present on profile fields per FR-6.

**2.2 — Schema: projects (structured intake)**
Dependencies: 2.1. Priority: P0. Complexity: S. Related: spec.md Section 6.2.

**2.3 — Schema: skills, skill_aliases, student_skills**
Dependencies: 2.1. Priority: P0. Complexity: M. Related: spec.md FR-14–16.
Acceptance: student_skills carries source (self-declared/resume-extracted/assessment-verified) and confidence per BR-1.

**2.4 — Schema: role_archetypes, role_archetype_skills**
Dependencies: 2.3. Priority: P0. Complexity: S. Related: spec.md FR-25.
Acceptance: essential-vs-optional distinction present per FR-25.

**2.5 — Schema: resumes, resume_analyses**
Dependencies: 2.1. Priority: P0. Complexity: M. Related: spec.md FR-8–13.

**2.6 — Schema: assessments, assessment_questions, assessment_attempts, assessment_answers**
Dependencies: 2.3. Priority: P0. Complexity: M. Related: spec.md FR-17–20.
Acceptance: full attempt history retained, not just latest (FR-18).

**2.7 — Schema: interviews, interview_questions, interview_answers**
Dependencies: 2.2, 2.4. Priority: P0. Complexity: M. Related: spec.md FR-40–45.

**2.8 — Schema: readiness_scores (historical), skill_gaps, recommendations, roadmap_tasks**
Dependencies: 2.3, 2.4, 2.6, 2.7. Priority: P0. Complexity: M. Related: spec.md FR-21–36, BR-2, BR-3.
Acceptance: readiness_scores append-only/historical; roadmap_tasks state enum includes skipped-by-student distinctly (FR-35).

**2.9 — Schema: memory_facts**
Dependencies: 2.1. Priority: P1. Complexity: S. Related: spec.md FR-7, Section 6.10.

**2.10 — Soft-delete + grace-period support**
Dependencies: 2.1. Priority: P0. Complexity: S. Related: spec.md FR-3, FR-4.

**2.11 — Seed data: skill taxonomy (MVP-scoped subset)**
Dependencies: 2.3. Priority: P0. Complexity: M. Related: spec.md FR-14, plan.md Section 5.
Acceptance: taxonomy limited to skills needed by MVP role archetypes + assessment bank; categories and known aliases populated.

**2.12 — Seed data: role archetypes (initial set)**
Dependencies: 2.4, 2.11. Priority: P0. Complexity: M. Related: spec.md FR-25–27.
Acceptance: at least the role archetypes needed to demonstrate SDE/data/QA/analyst coverage exist with essential/optional skill mappings.

---

## Phase 3 — Backend Foundation

**3.1 — AI Abstraction Layer interface**
Objective: build the single internal interface all modules use for LLM calls (plan.md Section 4).
Dependencies: 1.1. Priority: P0. Complexity: M.
Acceptance: exposes a task-typed completion interface; provider (Claude API) is swappable behind it; no other module imports a provider SDK directly.

**3.2 — Grounding-validation helper**
Objective: shared validation logic checking AI output is grounded in provided source text.
Dependencies: 3.1. Priority: P0. Complexity: M. Related: spec.md Section 8, plan.md Risks table.
Acceptance: unit-testable function/service that flags ungrounded content; used by Resume and Interview modules.

**3.3 — Rate limiting / cost control on AI-calling endpoints**
Dependencies: 3.1. Priority: P0. Complexity: M. Related: claude.md Security Principles.

---

## Phase 4 — Authentication

**4.1 — Google OAuth sign-in**
Dependencies: 2.1, 1.1. Priority: P0. Complexity: M. Related: spec.md FR-1.

**4.2 — Email/password sign-up/sign-in (fallback)**
Dependencies: 2.1. Priority: P0. Complexity: M. Related: spec.md FR-2.
Acceptance: passwords hashed per claude.md Security Principles; never logged/stored plaintext.

**4.3 — Session/token management**
Dependencies: 4.1, 4.2. Priority: P0. Complexity: M.

**4.4 — Authorization scoping (own-data-only enforcement)**
Dependencies: 4.3. Priority: P0. Complexity: M. Related: spec.md Section 11, Section 14.
Acceptance: cross-student access denial covered by tests.

---

## Phase 5 — Student Profile

**5.1 — Core profile CRUD**
Dependencies: 4.4, 2.1. Priority: P0. Complexity: S. Related: spec.md FR-5.

**5.2 — Field provenance tracking**
Dependencies: 5.1. Priority: P0. Complexity: S. Related: spec.md FR-6.

**5.3 — Structured project intake CRUD**
Dependencies: 5.1, 2.2. Priority: P0. Complexity: M. Related: spec.md Section 6.2.

**5.4 — Data export (student-facing)**
Dependencies: 5.1. Priority: P1. Complexity: S. Related: spec.md FR-3.

**5.5 — Account deletion flow (soft-delete + grace period)**
Dependencies: 2.10, 4.4. Priority: P1. Complexity: M. Related: spec.md FR-4.

---

## Phase 6 — Resume Intelligence

**6.1 — Resume upload (PDF/DOCX) + paste fallback**
Dependencies: 2.5, 5.1. Priority: P0. Complexity: M. Related: spec.md FR-8.
Acceptance: paste option surfaces automatically on parse failure, not just as a buried alternative.

**6.2 — Structured field extraction via AI Abstraction Layer**
Dependencies: 3.1, 3.2, 6.1. Priority: P0. Complexity: L. Related: spec.md FR-9, FR-10.
Acceptance: extraction output passes through grounding-validation (3.2); ungrounded fields flagged, not presented as fact.

**6.3 — Resume quality scoring**
Dependencies: 6.2. Priority: P0. Complexity: M. Related: spec.md FR-11.
Acceptance: score includes explanation of contributing factors.

**6.4 — AI-suggested rewrite generation**
Dependencies: 3.1, 3.2, 6.2. Priority: P0. Complexity: M. Related: spec.md FR-12, BR-4.
Acceptance: suggestions never introduce unsupported facts (validated via 3.2); no auto-apply exists anywhere in the flow.

**6.5 — Resume-to-role skill matching**
Dependencies: 6.2, 2.4. Priority: P0. Complexity: M. Related: spec.md FR-13.

---

## Phase 7 — Skill Intelligence

**7.1 — Skill taxonomy read/query API**
Dependencies: 2.11. Priority: P0. Complexity: S. Related: spec.md FR-14.

**7.2 — Student-skill record management (self-declared, resume-extracted, assessment-verified sources)**
Dependencies: 2.3, 6.5. Priority: P0. Complexity: M. Related: spec.md FR-15–16, BR-1.

---

## Phase 8 — Assessment Engine

**8.1 — Curated question bank content: initial set**
Objective: author an explicit, sized initial question bank (not open-ended) covering MVP-scope skills at multiple difficulty tiers.
Dependencies: 2.11. Priority: P0. Complexity: L. Related: spec.md FR-17.
Acceptance: minimum question-count-per-core-skill target defined and met (set concrete target during this task, e.g., per-skill minimum agreed before authoring begins).

**8.2 — Assessment session flow (attempt creation, timed/untimed)**
Dependencies: 2.6, 8.1. Priority: P0. Complexity: M. Related: spec.md FR-18–19.

**8.3 — Deterministic grading logic**
Dependencies: 8.2. Priority: P0. Complexity: M. Related: spec.md FR-17 (grading never LLM-judged).
Acceptance: unit tests cover grading logic with fixed expected outputs.

**8.4 — Assessment results → skill proficiency update**
Dependencies: 8.3, 7.2. Priority: P0. Complexity: M. Related: spec.md FR-20.

---

## Phase 9 — Placement Readiness

**9.1 — Deterministic readiness scoring formula implementation**
Dependencies: 6.3, 8.4, 2.8. Priority: P0. Complexity: L. Related: spec.md FR-21, BR-2.
Acceptance: formula documented and versioned; unit tests with fixed input→output cases.

**9.2 — Readiness factor breakdown/explanation output**
Dependencies: 9.1. Priority: P0. Complexity: M. Related: spec.md FR-22.

**9.3 — Readiness recalculation triggers**
Dependencies: 9.1. Priority: P0. Complexity: M. Related: spec.md FR-23.

**9.4 — Role-agnostic readiness fallback (no target role selected)**
Dependencies: 9.1. Priority: P1. Complexity: S. Related: spec.md FR-24.

**9.5 — Historical readiness score storage/retrieval**
Dependencies: 9.1, 2.8. Priority: P0. Complexity: S. Related: spec.md FR-46.

---

## Phase 10 — Job Intelligence (Role Archetypes)

**10.1 — Role archetype management (operator-side CRUD)**
Dependencies: 2.4, 2.12. Priority: P0. Complexity: S. Related: spec.md FR-25–26.

**10.2 — Role archetype selection (student-side)**
Dependencies: 10.1, 5.1. Priority: P0. Complexity: S. Related: user journey 4.3.

---

## Phase 11 — Skill Gap

**11.1 — Skill gap computation logic**
Dependencies: 7.2, 10.2. Priority: P0. Complexity: M. Related: spec.md FR-28.
Acceptance: unit tests with fixed cases.

**11.2 — Gap priority/urgency and explanation**
Dependencies: 11.1. Priority: P0. Complexity: M. Related: spec.md FR-29.

---

## Phase 12 — Recommendation Engine

**12.1 — Deterministic recommendation ranking logic**
Dependencies: 11.2, 9.2. Priority: P0. Complexity: M. Related: spec.md FR-30–31.
Acceptance: ranking is rule-based; unit tests with fixed cases; LLM not used for selection.

**12.2 — Recommendation phrasing via AI Abstraction Layer**
Dependencies: 3.1, 12.1. Priority: P1. Complexity: S. Related: spec.md FR-31 (LLM phrasing only, after selection).

**12.3 — Recommendation reasoning display data**
Dependencies: 12.1. Priority: P0. Complexity: S. Related: spec.md FR-32.

---

## Phase 13 — Adaptive Roadmap

**13.1 — Roadmap task generation from recommendations**
Dependencies: 12.1, 2.8. Priority: P0. Complexity: M. Related: spec.md FR-33.

**13.2 — Student override actions (accept/skip/reorder/add/remove)**
Dependencies: 13.1. Priority: P0. Complexity: M. Related: spec.md FR-34–35, BR-3.
Acceptance: skipped-by-student is a distinct, non-destructive state; not silently re-recommended without being distinguishable from a fresh suggestion.

**13.3 — Roadmap regeneration on signal change (non-destructive to actioned tasks)**
Dependencies: 13.2, 9.3. Priority: P0. Complexity: M. Related: spec.md FR-36.

---

## Phase 14 — AI Mentor

**14.1 — Mentor conversation endpoint (bounded scope, grounded in profile)**
Dependencies: 3.1, 5.1. Priority: P0. Complexity: L. Related: spec.md FR-37, FR-39.

**14.2 — Memory-fact extraction from conversation**
Dependencies: 3.1, 3.2, 14.1, 2.9. Priority: P0. Complexity: M. Related: spec.md FR-7, FR-38, Section 6.10.
Acceptance: no raw conversation transcript is stored/replayed as future context; only extracted structured facts are.

**14.3 — Memory-fact student-facing view/delete**
Dependencies: 14.2. Priority: P1. Complexity: S. Related: spec.md Section 6.10.

---

## Phase 15 — Mock Interview (General)

**15.1 — Question bank content: general technical + behavioral**
Dependencies: 2.11. Priority: P0. Complexity: L. Related: spec.md FR-40.

**15.2 — Interview session flow (question-by-question, text)**
Dependencies: 2.7, 15.1, 10.2. Priority: P0. Complexity: M. Related: spec.md FR-40.

**15.3 — Per-answer feedback + session scoring via AI Abstraction Layer**
Dependencies: 3.1, 15.2. Priority: P0. Complexity: L. Related: spec.md FR-41.

**15.4 — Interview results → readiness/skill signal update**
Dependencies: 15.3, 9.3, 7.2. Priority: P0. Complexity: M. Related: spec.md FR-42.

---

## Phase 16 — Project Defense Mode

**16.1 — Precondition check (structured project entry required)**
Dependencies: 5.3. Priority: P0. Complexity: S. Related: spec.md FR-43, BR-5.
Acceptance: clear explanatory message shown if unavailable.

**16.2 — Template/rule-driven question generation grounded in structured project fields**
Dependencies: 3.1, 3.2, 16.1. Priority: P0. Complexity: L. Related: spec.md FR-44.
Acceptance: every generated question traceable to specific structured field(s) it's grounded in.

**16.3 — Scoring/feedback (reuse general interview pattern)**
Dependencies: 16.2, 15.3. Priority: P0. Complexity: M. Related: spec.md FR-45.

---

## Phase 17 — Progress Dashboard

**17.1 — Historical progress data aggregation**
Dependencies: 9.5, 8.2, 13.2, 15.2. Priority: P0. Complexity: M. Related: spec.md FR-46.

**17.2 — Dashboard UI: readiness + explanation, top gaps, today's actions**
Dependencies: 17.1, 9.2, 11.2, 12.3. Priority: P0. Complexity: L. Related: spec.md Section 12.

**17.3 — Progress trend feeding back into recommendation logic**
Dependencies: 17.1, 12.1. Priority: P1. Complexity: M. Related: spec.md FR-47.

---

## Phase 18 — Company/Role Preparation Content

**18.1 — Curated preparation guidance content per role archetype**
Dependencies: 10.1. Priority: P1. Complexity: M. Related: spec.md FR-48.
Acceptance: content avoids unsupported claims about specific current company hiring patterns.

---

## Phase 19 — Admin

Not applicable to MVP scope (no admin/institutional accounts per claude.md Scope Boundaries). Operator-side role archetype/question-bank management (10.1, 8.1, 15.1) is handled as direct data-authoring/seed tasks, not a built admin UI, unless a lightweight internal tool is judged worth the time — flagged as P2 if pursued.

**19.1 (P2, optional) — Lightweight internal content-authoring tool for role archetypes/questions**
Dependencies: 10.1, 8.1. Priority: P2. Complexity: M.

---

## Phase 20 — Testing

**20.1 — Unit tests: deterministic scoring/ranking (readiness, skill gap, recommendation, grading)**
Dependencies: 9.1, 11.1, 12.1, 8.3. Priority: P0. Complexity: L. Related: spec.md Section 14, plan.md Section 9.

**20.2 — Grounding-validation tests (AI output rejection cases)**
Dependencies: 3.2, 6.4. Priority: P0. Complexity: M. Related: spec.md Section 14.

**20.3 — Integration test: full core loop end-to-end**
Dependencies: all of Phases 5–17. Priority: P0. Complexity: L. Related: spec.md Section 20 acceptance criteria.

**20.4 — Auth/authorization tests**
Dependencies: 4.4. Priority: P0. Complexity: M.

---

## Phase 21 — Security

**21.1 — File upload validation/sanitization (resume uploads)**
Dependencies: 6.1. Priority: P0. Complexity: M. Related: claude.md Security Principles.

**21.2 — Prompt-injection safeguards on user-supplied content fed to AI layer**
Dependencies: 3.1, 6.2, 14.1. Priority: P0. Complexity: M. Related: claude.md Security Principles.

**21.3 — Rate limiting / abuse prevention verification**
Dependencies: 3.3. Priority: P0. Complexity: S.

---

## Phase 22 — Deployment

**22.1 — Containerize backend and frontend build**
Dependencies: Phases 1–3 complete. Priority: P0. Complexity: M. Related: plan.md Section 10.

**22.2 — Single-environment cloud deployment (PaaS or VM + managed Postgres)**
Dependencies: 22.1. Priority: P0. Complexity: M.

**22.3 — Secrets management setup**
Dependencies: 22.2. Priority: P0. Complexity: S.

---

## Phase 23 — Advanced Features (Explicitly Post-MVP)

Not scheduled. Listed for traceability only, per spec.md Section 17:
- Voice-based mock interviews (STT/TTS)
- ML-based readiness prediction (pending real outcome data)
- AI-generated assessment questions for live grading
- Live external job-listing integration
- Institutional/B2B accounts and multi-tenancy
- Inactivity-based auto-purge policy

Do not begin any Phase 23 item without an explicit spec.md update authorizing it, per claude.md's Development Rules for Future Coding Agents.
