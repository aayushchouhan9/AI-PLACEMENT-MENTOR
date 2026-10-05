# claude.md — AI Placement Mentor: Persistent Project Context

This document is the persistent context for any human developer or AI coding agent working on this project. Read this first, before `spec.md`, `plan.md`, or `tasks.md`. If anything in those three documents ever appears to conflict with the principles here, treat that as a bug to flag, not a decision to resolve silently.

## Relationship Between the Four Documents

- **claude.md** (this file) — persistent context. Vision, principles, constraints, and rules that should not change often. Read this to understand *why* the project is shaped the way it is.
- **spec.md** — defines **WHAT** must be built. Functional and non-functional requirements, modules, business rules, acceptance criteria.
- **plan.md** — defines **HOW** it should be built. Architecture, phased implementation strategy, technology decisions, risks.
- **tasks.md** — defines the **concrete units of work**. Broken into phases with task IDs, dependencies, and acceptance criteria.

Order of authority when in doubt: `claude.md` principles constrain `spec.md`; `spec.md` requirements constrain `plan.md`; `plan.md` strategy constrains `tasks.md`. A task should never introduce a requirement not traceable to spec.md. A spec requirement should never violate a claude.md principle.

## Project Vision

AI Placement Mentor is a personal, continuously-learning placement-preparation mentor for college engineering students (tech-adjacent roles). It is not a chatbot wrapper. Its core value is the closed loop:

```
Profile + Resume + Projects → Skill Assessment → Readiness Analysis → Target Role →
Skill Gap Analysis → Recommendations → Adaptive Roadmap → Practice + Mock Interview →
Performance Analysis → Updated Profile → Updated Recommendations
```

Every module exists to feed or consume this loop. A feature that doesn't connect to it does not belong in this product.

## Product Philosophy

1. **Mentor, not oracle.** The system advises; the student decides. Recommendations must always be explainable and overridable — never a silent black box the student must simply obey.
2. **Correctness over AI-for-its-own-sake.** Every "intelligent" feature must justify why it needs an LLM/ML versus a deterministic rule, database query, or simple scoring formula. Default to the simplest reliable mechanism.
3. **Never fabricate.** No invented facts on a resume. No invented model accuracy. No invented job-market claims. No invented skills a student never demonstrated. If data doesn't exist to support a claim, the system says so — it doesn't guess and present the guess as fact.
4. **Explainability is a feature, not a nice-to-have.** Readiness scores, skill gaps, and recommendations must always show their contributing factors. "Trust me" is not an acceptable UX for any scoring output.
5. **Individual-first.** Built for individual students today (see Scope Boundaries). Institutional/B2B is a real, intended future direction — but is never allowed to leak complexity into the MVP build.
6. **Tech-adjacent scope only.** Software/CS-track and other engineering-branch students pursuing SDE, data, QA, analyst-type roles. Not core-branch domain-specific placement (e.g., mechanical site engineering interviews). Do not scope-creep into this.

## Scope Boundaries (Read Before Adding Any Feature)

| In scope for the product's stated direction | Explicitly out of scope until stated otherwise |
|---|---|
| Individual student accounts | Institutional/college/admin/recruiter accounts, multi-tenant orgs |
| Tech-adjacent roles (SDE, data, QA, analyst) | Core-branch domain-specific interviews (mechanical, civil, EE core) |
| Text-based mock interviews | Voice-based interviews (STT/TTS) |
| Rule-based, explainable readiness scoring | ML-predicted readiness (no labeled outcome data exists yet) |
| Curated skill-assessment question bank | AI-generated assessment questions used for live grading |
| Manually curated role-archetype job data | Live external job-listing API integration, scraping |
| AI-suggested resume rewrites (opt-in, rephrase-only) | Fully autonomous resume rewriting/generation |
| "Career Twin" concept | **Dropped entirely** — fully redundant with Student Profile + Readiness Score + Skill Gaps. Do not reintroduce without a genuinely distinct capability being defined first. |

If a future task or feature request falls into the "out of scope" column, flag it rather than silently implementing it.

## AI/ML Principles

1. **Provider-agnostic by design.** All LLM calls go through an internal AI abstraction layer. No module calls a specific provider's SDK directly. Default provider: Claude API. Must remain swappable.
2. **Deterministic where possible.** Readiness scoring, skill-gap calculation, and grading of curated assessment questions are rule-based/deterministic — not LLM judgment calls — for MVP. This is a hard constraint, not a starting-point-to-be-abandoned-early.
3. **LLM roles are bounded.** Where an LLM is used (resume-suggestion phrasing, mentor conversation, structured resume-field extraction, project-defense question generation grounded in structured project data, mock-interview answer feedback), it operates on a narrowly scoped task with validation of its output against source data — not as an open-ended agent.
4. **No invented facts, ever.** Any AI-generated content that touches resume text, project descriptions, or feedback must be checked against the source the student actually provided. This is the single most important AI safety rule in this codebase — resume rewrite suggestions may rephrase, never invent achievements, metrics, or experience.
5. **Structured memory, not raw transcript replay.** The AI Mentor does not retain or replay full conversation history as context. It extracts discrete "memory facts" (e.g., "struggles with DP," "prefers backend roles") into the structured student profile, and future interactions are grounded in that structured profile — not in re-fed unvalidated chat logs. This bounds context growth, cost, and prompt-injection surface area.
6. **ML is a documented future phase, not a current pretense.** Readiness prediction, embeddings-based matching, and any other classical-ML/embedding feature require real outcome data that does not exist yet at project start. Do not fabricate model performance numbers. Do not claim predictive accuracy without an evaluation dataset. The path is: Phase 1 (transparent rules) → Phase 2 (collect legitimate data, including actual placement outcomes) → Phase 3 (train and evaluate a real model, only if justified by data quality and problem fit).
7. **Never trust an LLM for correctness grading of factual/technical questions** in MVP. Curated question banks with known-correct answers are the grading source of truth.

## Security Principles

- Passwords (for the email/password fallback path) hashed with a modern algorithm (e.g., bcrypt/argon2); never stored or logged in plaintext.
- Google OAuth is the primary auth path; treat OAuth tokens with the same care as credentials.
- All file uploads (resumes) are treated as untrusted input: validate file type/size, scan for malformed content, never execute uploaded content, isolate parsing from the rest of the system where feasible.
- Prompt-injection awareness: resume content, project descriptions, and any user-supplied text that gets fed into an LLM prompt is untrusted input. Never let uploaded document content override system instructions to the AI abstraction layer.
- Rate limiting and abuse prevention on all AI-calling endpoints (mentor chat, resume analysis, mock interview, assessment generation) — these are the most cost-exposed and abuse-exposed surfaces.
- Standard API security: authenticated endpoints by default, authorization checks scoped to the requesting student's own data, no direct object reference vulnerabilities (a student must never be able to fetch another student's resume/profile/interview data by guessing an ID).

## Privacy Principles

- **Data minimization.** Only collect what a defined feature actually uses.
- **Student owns their data.** View, export, and delete are first-class capabilities, not backlog items.
- **Soft-delete with grace period.** Account deletion is a soft-delete with a defined grace period (e.g., 30 days) before permanent purge, giving the student a genuine chance to reconsider. No automatic inactivity-based purging in MVP (documented as a future policy, not built).
- **No institutional access model in MVP.** Because there is no institutional/admin account type in MVP, there is no institutional-override or FERPA-style institutional-access design needed yet. This will need real design work if/when the B2B phase happens — do not assume today's privacy model transfers unchanged.

## Development Rules for Future Coding Agents

1. **Do not add multi-tenant/organization tables, roles, or admin dashboards** unless spec.md is explicitly updated to include the B2B phase. The system should remain *tenant-agnostic-ready* as a design principle (e.g., don't hardcode "one global user table with no notion of grouping" in a way that would force a painful migration) — but this means keeping the door open architecturally, not building the room today.
2. **Do not introduce voice/STT/TTS infrastructure** for mock interviews unless spec.md is explicitly updated.
3. **Do not build or wire up an ML training pipeline or a "readiness prediction model"** unless a real, legitimately obtained, labeled outcome dataset exists and is documented. Log the raw signals now (assessment scores, resume scores, interview scores, task completion, and — when available — actual placement outcomes) so a future ML phase is *possible*, but do not build the model itself.
4. **Do not let the AI Mentor become an open-ended chatbot.** Every mentor interaction should be groundable in the student's structured profile/data. If a coding agent finds itself building generic unscoped chat memory or unrestricted conversation history replay, stop — that contradicts principle 5 under AI/ML Principles.
5. **Do not auto-apply AI resume suggestions.** The student must explicitly accept each suggested rewrite. Do not build a "one-click apply all" that bypasses per-suggestion review.
6. **Do not trust AI-generated content as a source of graded correctness.** Curated question banks are the grading authority for assessments in MVP.
7. **Keep the AI provider call surface behind the abstraction layer.** Any new AI-touching feature should call the abstraction layer's interface, not a provider SDK directly.
8. **When in doubt about scope, check the Scope Boundaries table above** before implementing a feature that seems adjacent to something already in scope.

## Technology Decisions (Summary — see plan.md for detail)

- Frontend: React
- Backend: FastAPI (Python) — chosen specifically because future ML/data-science work (model training, embeddings, pandas-based analysis) should be native to the backend rather than bolted on via a separate service
- Database: PostgreSQL
- Cache: Redis (introduced when a real caching need is identified — see plan.md)
- Vector database: not introduced in MVP; no current requirement justifies it
- AI provider: Claude API by default, behind a provider-agnostic abstraction layer
- Auth: Google OAuth (primary) + email/password (fallback)
- Deployment: single-environment pragmatic cloud deployment (containerized), not premature production-grade multi-environment infra
- Architecture style: modular monolith, not microservices

## What "Done" Looks Like for MVP

The full closed loop — profile/project intake → resume analysis → skill assessment → rule-based readiness scoring → role-archetype-based skill gap analysis → recommendations → student-overridable adaptive roadmap → memory-grounded AI mentor → text-based mock interview (generic + project defense) — is functional end-to-end for a single student, with explainable outputs at every scoring step, and with the AI layer bounded and provider-agnostic as described above. See spec.md for the full MVP feature list and acceptance criteria.
