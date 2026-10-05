# plan.md — AI Placement Mentor: Implementation Plan

Defines **HOW** spec.md gets built. No source code in this document. See `claude.md` for principles, `spec.md` for requirements, `tasks.md` for the concrete task breakdown.

---

## 1. Architecture Overview

**Style: Modular monolith.** Rejected microservices and premature serverless/event-driven decomposition for MVP — the team size (individual/small), the tight coupling between modules in the core loop (readiness score depends on resume + assessment + interview + roadmap signals simultaneously), and the "don't overengineer" constraint all argue against distributed-systems overhead this early. The monolith is structured into clearly bounded internal modules (see Section 3) so it *can* be decomposed later if real scaling pressure appears — but that's a documented option, not a current task.

```
                        ┌─────────────────────────┐
                        │   React Frontend (SPA)   │
                        └────────────┬─────────────┘
                                     │ REST (HTTPS)
                        ┌────────────▼─────────────┐
                        │   FastAPI Backend         │
                        │   (modular monolith)      │
                        │                            │
                        │  ┌──────────────────────┐ │
                        │  │ Auth Module           │ │
                        │  │ Profile Module         │ │
                        │  │ Resume Module          │ │
                        │  │ Skill Module           │ │
                        │  │ Assessment Module      │ │
                        │  │ Readiness Module       │ │
                        │  │ Role/Job Module        │ │
                        │  │ Skill Gap Module       │ │
                        │  │ Recommendation Module  │ │
                        │  │ Roadmap Module         │ │
                        │  │ Mentor Module          │ │
                        │  │ Interview Module       │ │
                        │  │ AI Abstraction Layer   │◄├──► LLM Provider (Claude API, swappable)
                        │  └──────────────────────┘ │
                        └────────────┬───────────────┘
                                     │
                        ┌────────────▼─────────────┐
                        │   PostgreSQL (primary)    │
                        └────────────────────────────┘
                        ┌────────────────────────────┐
                        │   Redis (cache — added     │
                        │   when a real need exists) │
                        └────────────────────────────┘
```

## 2. Technology Stack (Decisions and Rationale)

| Layer | Choice | Rationale |
|---|---|---|
| Frontend | React | Standard, well-supported, matches team familiarity assumed from decision process |
| Backend | FastAPI (Python) | Async-capable, strong typing via Pydantic (useful for structured LLM output schemas), and — critically — Python is the natural home for any future ML/embeddings work, keeping that work in-process rather than a bolted-on separate service later |
| Database | PostgreSQL | Relational integrity fits the strongly relational domain (students, skills, roles, assessments, attempts); mature, well-understood, works well with FastAPI/SQLAlchemy |
| Cache | Redis | Introduced only once a concrete caching need is identified (e.g., role-archetype/skill-taxonomy read-heavy endpoints, rate-limit counters) — not provisioned speculatively on day one |
| Vector DB | None in MVP | No current requirement (no live job-listing semantic search, no embeddings-based matching) justifies the operational overhead; revisit if/when embeddings-based skill matching becomes a real, data-justified feature |
| AI Provider | Claude API (default), behind an internal AI abstraction layer | Provider-agnostic per claude.md; abstraction layer means swapping providers later doesn't touch feature code |
| Auth | Google OAuth (primary) + email/password (fallback) | Matches target user (college students, near-universal Google usage) while avoiding a single-provider lock-in risk |
| Deployment | Single-environment containerized cloud deployment (e.g., a basic PaaS or single VM + managed Postgres) | Pragmatic for portfolio-project scale; containerization keeps a path open to more mature infra later without over-investing now |

## 3. Module Boundaries (Backend)

Each module below is a bounded internal package with a defined interface — this is what "modular" means in "modular monolith." No module reaches directly into another module's database tables; cross-module data access goes through the owning module's service interface.

1. **Auth** — signup/login (OAuth + password), session/token issuance, password hashing.
2. **Profile** — core student profile fields, field provenance tracking, structured project intake.
3. **Resume** — upload/parse/paste ingestion, LLM-based structured extraction with grounding validation, resume quality scoring, opt-in suggested rewrites.
4. **Skill** — canonical taxonomy, student-skill records with source/confidence, alias resolution.
5. **Assessment** — curated question bank, attempt sessions, deterministic grading, results feeding into Skill module.
6. **Readiness** — deterministic weighted scoring, historical score storage, explanation/breakdown generation.
7. **Role/Job** — role archetype CRUD (operator-maintained), essential/optional skill mappings.
8. **Skill Gap** — computes gap between student skills (Skill module) and target role requirements (Role module).
9. **Recommendation** — rule-based ranking of next actions from Skill Gap + Readiness + Roadmap state; LLM used only for phrasing an already-selected recommendation.
10. **Roadmap** — task generation from recommendations, student override handling (accept/skip/reorder/add/remove), task-state tracking.
11. **Mentor** — bounded conversational interface; extracts memory facts into Profile module; grounds responses in structured profile data.
12. **Interview** — general mock interview (curated bank) and project-defense mode (grounded in Profile's structured project data); scoring/feedback; results feed Readiness and Skill modules.
13. **AI Abstraction Layer** — single internal interface all modules call for any LLM interaction; owns provider selection, prompt templating, grounding-validation helpers, and rate-limit/cost controls. No feature module calls a provider SDK directly.

## 4. AI Integration Strategy

- **Abstraction layer contract:** a single internal service (e.g., `ai_client.complete(task_type, structured_input) -> structured_output`) that internally selects the provider, applies the correct prompt template for the `task_type`, and — for tasks with grounding requirements (resume extraction, resume suggestions, project-defense question generation) — runs the output through a grounding-validation step before returning it to the calling module.
- **Grounding validation:** for resume extraction/suggestions, validate that extracted/suggested content maps back to substrings or clearly paraphrased content of the source text; flag or reject ungrounded output rather than passing it through. (Grounded in the research finding that LLM-based extraction's main failure mode is exactly this kind of unsupported normalization/invention.)
- **Structured output:** use schema-constrained prompting (e.g., Pydantic-model-defined expected JSON shape) for all structured extraction tasks (resume fields, project-defense question grounding references) rather than free-form text parsing — reduces downstream parsing fragility.
- **Cost/rate control:** the abstraction layer is the natural place to enforce per-student rate limits and cost budgets across all AI-calling endpoints (mentor chat, resume analysis, interview feedback), since every call funnels through it.
- **Task types requiring the abstraction layer (MVP):** resume field extraction, resume rewrite suggestions, resume quality-score explanation phrasing, recommendation phrasing, mentor conversation turns, memory-fact extraction from mentor conversations, project-defense question generation (template-grounded), mock-interview answer feedback generation.
- **Task types that must NOT use the AI layer for their core logic (deterministic only):** readiness score computation, skill gap computation, recommendation *selection*/ranking, assessment grading.

## 5. Database Strategy

- **Database-first approach for MVP build order:** define and migrate the schema before building feature endpoints against it, since nearly every module depends on shared entities (students, skills, role archetypes).
- **Historical, not overwritten, scoring data:** readiness_scores, skill_gaps snapshots, and assessment/interview attempt records are append-only/historical, not update-in-place — this is required both by spec.md (progress tracking, BR-2) and is a prerequisite for any future ML phase.
- **Provenance fields:** any table representing a "fact" about a student (skills, profile fields) carries a source/provenance column per spec.md FR-6.
- **Soft-delete:** account-level soft-delete with a `deletion_requested_at` / grace-period-expiry timestamp; a scheduled job (simple, not elaborate) permanently purges past the grace period.
- **Tenant-agnostic-readiness (no build):** avoid schema choices that assume exactly one global unscoped user pool in a way that would be painful to retrofit (e.g., prefer designs where a future `organization_id` nullable foreign key *could* be added later without restructuring core tables) — but do not add an organizations table or any tenant-scoping logic now.
- **Skill taxonomy seeding:** seed data structured with skill categories, aliases, and essential/optional-per-role-archetype mappings — a lightweight, MVP-scoped structure inspired by (not imported wholesale from) established public skill-taxonomy patterns (category hierarchy, essential-vs-optional skills per occupation), per the research conducted during brainstorming.

## 6. Backend Strategy

- Build in dependency order: Auth → Profile → Skill taxonomy (seed data) → Role archetypes (seed data) → Resume → Assessment → Readiness → Skill Gap → Recommendation → Roadmap → Mentor → Interview (general) → Interview (project defense).
- Each module exposes a service-layer interface consumed by its own API routes and, where needed, by other modules' service layers directly (not via internal HTTP calls — this is a monolith, in-process calls are appropriate).
- Deterministic scoring modules (Readiness, Skill Gap, Recommendation ranking) are built and unit-tested before their outputs are wired into UI-facing endpoints, since they are the highest-trust, highest-test-value parts of the system.

## 7. Frontend Strategy

- Single-page React app, dashboard-first (per spec.md Section 12).
- Every scored/ranked/AI-influenced component fetches and renders an accompanying explanation payload — this should be a shared UI pattern/component (e.g., a reusable "why this score/recommendation" expandable panel) rather than reimplemented per feature.
- Resume suggestion review, roadmap task management, and mock interview flows are the three most interaction-heavy UI surfaces and should be prioritized for solid UX over the more passive dashboard/read-only views.

## 8. AI/ML Strategy (Phased)

**Phase 1 (MVP — this build):** Fully deterministic, transparent scoring for readiness, skill gaps, and recommendation ranking. LLM used only for bounded, validated language tasks (extraction, phrasing, conversation, question generation) as detailed in Section 4. No model training, no prediction.

**Phase 2 (future, not built now):** Once the product has real usage and — critically — real placement outcome data becomes available (e.g., students self-report offers/outcomes, or another legitimate data-collection mechanism is designed), begin evaluating whether that data is sufficient in volume and quality to support classical ML (not necessarily deep learning) for readiness prediction or recommendation personalization. This phase explicitly requires a documented data-collection design before any modeling work starts.

**Phase 3 (future, not built now):** If Phase 2 data proves sufficient, train and rigorously evaluate a real model (train/validation/test split, documented metrics, no fabricated performance claims), and only then consider replacing or augmenting the Phase 1 deterministic score — likely as an *additional* signal shown alongside the explainable score, not a silent replacement, to preserve the explainability principle.

## 9. Testing Strategy

- Unit tests: all deterministic scoring/ranking logic (Readiness, Skill Gap, Recommendation), with fixed input→expected-output test cases — highest priority given these are the most trust-critical, most explainability-dependent parts of the system.
- Grounding-validation tests: specific tests asserting that ungrounded/fabricated AI output (e.g., a resume suggestion introducing a metric not in the source) is caught and rejected by the AI Abstraction Layer's validation step.
- Integration tests: full core-loop walkthrough (profile → resume → assessment → readiness → gap → recommendation → roadmap → interview → updated readiness) as an end-to-end scenario.
- Auth/authorization tests: cross-student data-access denial, soft-delete grace-period behavior.
- See tasks.md Phase 20 for concrete testing tasks.

## 10. Deployment Strategy

- Containerize the FastAPI backend and (build step for) the React frontend.
- Single environment for MVP: one deployment target (a basic PaaS like Render/Railway/Fly.io-class platform, or a single VM) plus a managed PostgreSQL instance.
- No multi-environment (staging/prod) split, no full CI/CD pipeline, and no dedicated observability stack in MVP — documented explicitly as future infra maturity work, not current tasks, per claude.md and spec.md Section 15.
- Secrets (OAuth client secrets, AI provider API keys, DB credentials) managed via the deployment platform's environment-variable/secrets mechanism — never committed to source control.
- Basic rate limiting implemented at the application layer (in the AI Abstraction Layer, per Section 4) rather than requiring dedicated infra for MVP.

## 11. Migration Strategy

Not applicable at MVP scope (greenfield project, single environment, no legacy data to migrate). If/when a B2B/multi-tenant phase begins, that phase must include a dedicated migration plan for retrofitting organization scoping onto existing single-tenant data — flagged here so it isn't forgotten, not designed now.

## 12. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| LLM-based resume extraction hallucinating/inventing fields | Grounding-validation step in AI Abstraction Layer (Section 4); never present ungrounded extraction as fact (spec.md FR-10) |
| AI resume suggestions introducing fabricated achievements | Same grounding-validation step, plus mandatory per-suggestion explicit accept (spec.md FR-12, BR-4) — no auto-apply |
| Readiness score feeling like a black box, eroding trust | Deterministic formula with mandatory factor breakdown on every computation (spec.md FR-22); documented, versioned formula (BR-2) |
| Cost overrun from uncontrolled LLM calls (mentor + resume + interview all calling out) | Rate limiting/cost budget enforced centrally in AI Abstraction Layer; mentor uses structured memory facts instead of full-history replay to bound prompt size |
| Curated question bank content being too small to be useful at launch | Explicitly scope initial question-bank size as a concrete tasks.md deliverable rather than leaving it open-ended (see tasks.md Phase 8) |
| Project Defense Mode producing shallow/generic questions | Mandated structured project intake (spec.md Section 6.2) as a prerequisite; template/rule-grounded question generation tied to specific fields (FR-44), not free-form speculation |
| Scope creep into institutional/B2B, voice interviews, or ML prediction before they're justified | Explicit Scope Boundaries table in claude.md; development rules instructing future coding agents to check spec.md before building adjacent-seeming features |
| Overengineering the architecture for a portfolio-scale project | Modular monolith decision (Section 1); Redis/vector DB introduced only on demonstrated need, not speculatively |
| Skill taxonomy scope creep (importing thousands of irrelevant skills) | Seeding strategy explicitly scoped to MVP role archetypes + assessment bank needs only (Section 5), informed by but not copied from ESCO/O*NET-style structures |
