# spec.md — AI Placement Mentor: Product Specification

Defines **WHAT** must be built. See `claude.md` for the principles this spec must honor, `plan.md` for **HOW** it gets built, and `tasks.md` for the concrete work breakdown.

---

## 1. Product Overview

AI Placement Mentor is a web application that acts as a personal placement-preparation mentor for individual college engineering students targeting tech-adjacent roles (SDE, data, QA, analyst-type positions). It continuously analyzes a student's profile, resume, projects, and skill/interview performance to produce an explainable placement-readiness score, identify skill gaps against role archetypes, generate a personalized and student-controllable roadmap, and provide text-based mock interviews (including project-specific "defense" interviews) with AI-assisted feedback.

## 2. Goals

- Give a student a single, trustworthy, explainable answer to "how ready am I, for what, and what should I do next?"
- Replace generic prep advice with prep grounded in the student's actual resume, project depth, and measured skill performance.
- Keep every AI-touching feature bounded, explainable, and free of fabricated facts.
- Ship an MVP that is realistically buildable by a small team/individual in a portfolio-project timeframe.

## 3. Users

- **Primary user (MVP):** an individual engineering student (any branch) targeting a tech-adjacent role, self-registering and using the product solo.
- **Not a user in MVP:** placement officers, college admins, recruiters. (Reserved for a documented future B2B phase — see Section 15.)

## 4. User Journeys

### 4.1 Onboarding
1. Student signs up (Google OAuth or email/password).
2. Student completes core profile fields (education, target role interest — optional at this stage, branch, graduation year).
3. Student uploads or pastes their resume.
4. Student adds structured project entries (see Section 6.2).
5. System produces an initial (necessarily partial/low-confidence) readiness snapshot and explains what's missing to improve confidence (e.g., "complete a skill assessment to improve accuracy").

### 4.2 Ongoing Use Loop
1. Student lands on a dashboard showing current readiness score (with explanation), top skill gaps, and today's recommended actions.
2. Student takes a skill assessment, works through roadmap tasks, chats with the AI mentor, or takes a mock interview.
3. Each activity updates the student's profile/signals.
4. Readiness score, skill gaps, recommendations, and roadmap update accordingly, with the change explained (what changed and why).

### 4.3 Target Role Selection
1. Student browses or searches role archetypes (e.g., "SDE-1 Backend," "Data Analyst," "QA Engineer").
2. Student selects a target role (can change it later; can also have no target selected, in which case the system shows role-agnostic core-skill guidance only).
3. System runs skill-gap analysis against the selected role archetype's required skills.

### 4.4 Mock Interview
1. Student chooses interview type: general technical, general behavioral, or project defense (must have at least one structured project entry to use project defense).
2. System generates/selects questions (curated bank for general; structured-data-grounded templates for project defense).
3. Student answers in text, one question at a time.
4. System scores/gives feedback per answer and an overall session summary, with explanation.
5. Results feed back into the student's profile and readiness signals.

## 5. Functional Requirements

### 5.1 Authentication & Account
- FR-1: Support Google OAuth sign-in.
- FR-2: Support email/password sign-up/sign-in as a fallback, with secure password hashing.
- FR-3: Student can view, export (machine-readable format, e.g. JSON), and delete their own data.
- FR-4: Account deletion is a soft-delete with a configurable grace period (default 30 days) before permanent purge; student can cancel deletion within the grace period.

### 5.2 Student Profile
- FR-5: Core profile fields: name, email, branch/department, graduation year, target role (optional, changeable, nullable).
- FR-6: Profile distinguishes field provenance: user-entered vs. extracted-from-resume vs. AI-inferred vs. calculated (e.g., readiness score is calculated, a listed skill from resume is extracted, a mentor-derived preference is AI-inferred).
- FR-7: Structured "memory facts" derived from AI Mentor conversations are stored as part of the profile (see Section 6.10), each with a source (which conversation/date) and are student-viewable and student-deletable individually.

### 5.3 Resume Intelligence
- FR-8: Support resume upload as PDF or DOCX, and a plain-text paste fallback (system must never block a student from proceeding due to a parsing failure — paste is always available).
- FR-9: Extract structured fields (contact info, education, work/internship experience, skills, projects-as-listed) using LLM-based structured extraction against a defined schema.
- FR-10: Every extracted field must be traceable back to source text; extraction that cannot be grounded in the source resume text must not be presented as extracted fact.
- FR-11: Resume quality scoring: evaluate completeness, clarity, and job-relevance (against target role, if set), with an explanation of the score's contributing factors.
- FR-12: AI-suggested rewrites for bullet-point phrasing: system may propose rephrased text for clarity/impact; each suggestion is shown individually with an Accept/Reject action; nothing is auto-applied. Suggestions must only rephrase existing content — never introduce a fact, metric, or achievement not present in the student's original text. This is validated (see Section 8, AI Requirements).
- FR-13: Resume-to-job matching: compare extracted resume skills against the selected target role archetype's required skills, feeding into skill-gap analysis (Section 5.6).

### 5.4 Skill Intelligence
- FR-14: Maintain a canonical skill taxonomy: skill name, category (e.g., Technical, Core CS, Tools, Soft Skills), aliases (e.g., "JS" → "JavaScript"), and optional prerequisite relationships. Seeded only with skills actually needed for MVP's role archetypes and assessment bank (not an oversized import).
- FR-15: Each skill entry a student has is tracked with: proficiency level, confidence, and source (self-declared, resume-extracted, or assessment-verified).
- FR-16: Assessment-verified skills carry higher confidence than self-declared or resume-extracted ones in downstream scoring.

### 5.5 Assessment Engine
- FR-17: Curated question bank (MCQ, short technical/coding problems) organized by skill and difficulty. Question correctness/grading logic is deterministic and bank-defined — never LLM-judged for MVP.
- FR-18: Support timed and untimed assessment attempts; store full attempt history (not just latest score).
- FR-19: Adaptive difficulty within an assessment session is optional/future-considered; MVP requires at minimum fixed-difficulty assessments per skill with multiple difficulty tiers a student can choose or be recommended.
- FR-20: Assessment results update the corresponding skill's proficiency/confidence on the student's profile.

### 5.6 Placement Readiness
- FR-21: Compute a placement readiness score using a deterministic, weighted, documented formula combining: resume quality score, skill assessment results (verified skills vs. target role requirements), roadmap/task completion, and mock interview performance.
- FR-22: The readiness score output must always include a breakdown showing each contributing factor's value and weight — no opaque single number without explanation.
- FR-23: Readiness score recalculates whenever a contributing signal changes (new assessment result, resume update, interview completed, roadmap task completed).
- FR-24: If no target role is selected, readiness is shown as a general/role-agnostic score with a prompt to select a target role for role-specific readiness.

### 5.7 Job/Role Intelligence
- FR-25: Maintain a manually curated set of role archetypes (e.g., "SDE-1 Backend," "SDE-1 Frontend," "Data Analyst," "QA Engineer") each with: description, essential required skills, optional/nice-to-have skills (mirroring the essential-vs-optional pattern used by standard skill taxonomies), and typical experience-level expectations.
- FR-26: Role archetypes are structured data maintained by the system operator, not sourced from live external job listings or scraping in MVP.
- FR-27: Live external job-listing integration is explicitly out of scope for MVP (see claude.md Scope Boundaries) but role archetype data structures should not preclude adding a "sourced from listing X, last synced on Y" field later.

### 5.8 Skill Gap Analysis
- FR-28: For a student with a selected target role, compute the gap between the student's current verified/declared skills and the role archetype's required skills.
- FR-29: Each gap entry includes: skill name, current proficiency (or "none"), required proficiency, priority/urgency (derived from whether the skill is essential vs. optional for the role, and from the size of the gap), and an explanation of why it's prioritized as such.

### 5.9 Recommendation Engine
- FR-30: Given the current skill gaps, readiness breakdown, and roadmap state, generate ranked "what to do next" recommendations (e.g., "take the Assessment for X," "complete roadmap task Y," "attempt a mock interview").
- FR-31: Recommendation logic for MVP is rule/scoring-based (e.g., rank by gap priority × estimated effort × recency of last activity on that skill) — not an LLM freeform suggestion generator. An LLM may be used only to phrase/explain a recommendation already selected by the deterministic ranking, never to select which recommendation to surface.
- FR-32: Recommendations must show their reasoning (why this, why now).

### 5.10 Adaptive Roadmap
- FR-33: Generate a roadmap of tasks (e.g., "complete X assessment," "study topic Y," "attempt project defense mock interview") derived from skill gaps and recommendations.
- FR-34: Student can accept, skip, reorder, or manually add/remove roadmap tasks.
- FR-35: Task state includes at minimum: pending, in-progress, completed, skipped-by-student. Skipped tasks are recorded as a distinct state (not deleted, not treated as "done") so future recommendations account for the student's actual choices.
- FR-36: Roadmap regenerates/adjusts recommended-but-not-yet-actioned tasks when underlying skill gaps or readiness change, without silently discarding student overrides on tasks already actioned.

### 5.11 AI Mentor
- FR-37: Conversational interface where the student can ask placement-related questions and receive guidance grounded in their own profile/data.
- FR-38: The mentor does not retain or replay raw conversation transcripts as context for future sessions. It extracts structured "memory facts" (see FR-7) from conversations, and future sessions are grounded in the structured profile, not in past chat logs.
- FR-39: The mentor's scope is bounded to placement-preparation topics grounded in the student's data; it is not a general-purpose open-ended chatbot.

### 5.12 Mock Interview (General)
- FR-40: Text-based mock interview sessions, question-by-question, covering general technical and/or behavioral questions drawn from a curated bank (with question selection informed by target role and skill gaps).
- FR-41: Per-answer feedback and an end-of-session summary score with explanation.
- FR-42: Interview results (per-question and session-level) are stored in full history and feed into readiness scoring (FR-21) and skill confidence updates where applicable.

### 5.13 Mock Interview (Project Defense Mode)
- FR-43: Requires the student to have at least one structured project entry (Section 6.2 fields) — a resume one-liner is not sufficient input.
- FR-44: Generates interview questions about the student's own project — architecture, technology choices, database, algorithms, challenges, trade-offs, scalability, limitations — grounded in the structured fields the student provided (template/rule-driven question construction from structured input), not free-form AI speculation about an under-specified project.
- FR-45: Scoring/feedback follows the same pattern as general mock interview (FR-41).

### 5.14 Progress Tracking
- FR-46: Track historical readiness scores, assessment attempts, roadmap task completion, and mock interview sessions over time (not just latest state) so the student can see a trend.
- FR-47: Progress data feeds recommendations (e.g., deprioritize a skill area with sustained improvement; reprioritize one with repeated failure).

### 5.15 Company/Role Preparation Content
- FR-48: For each role archetype, provide structured preparation guidance (what's typically evaluated, common topics) as curated content — not claims about live/current specific-company hiring patterns, which are explicitly avoided (no unsupported claims about current company-specific hiring behavior).

## 6. Detailed Module Notes

### 6.1 Resume Upload
Accepted formats: PDF, DOCX. A "paste your resume text" option must always be available and must be presented proactively if upload/parse fails, not just as a hidden fallback.

### 6.2 Structured Project Intake
Per project, required fields: project name, one-line summary, your specific role, tech stack (list), key architectural/design decisions (free text), challenges faced (free text), trade-offs made (free text). This is a first-class MVP module — not an implicit sub-feature of resume parsing — because Project Defense Mode (FR-43–45) depends on it.

### 6.10 Memory Facts
A memory fact record includes: fact text, category (e.g., skill-struggle, role-preference, learning-style), source conversation reference, date created, and a student-facing delete action. Memory facts inform mentor responses and may inform recommendations, but must never be presented as verified skill data (that comes only from FR-16's assessment-verified path).

## 7. Business Rules

- BR-1: A skill's confidence ranking, highest to lowest: assessment-verified > resume-extracted > self-declared.
- BR-2: Readiness score weighting and formula must be documented and versioned; changes to the formula must be explainable to a student comparing scores over time (e.g., "the scoring formula was updated on [date]" rather than an unexplained jump).
- BR-3: A roadmap task marked skipped-by-student is never silently resurrected as a new "recommended" task without being distinguishable from a fresh recommendation (avoid nagging the student about something they deliberately deprioritized, while still allowing it to reappear if circumstances materially change, e.g., they changed target role).
- BR-4: AI-generated resume suggestions are never auto-applied; acceptance is an explicit per-suggestion student action.
- BR-5: Project Defense Mode is unavailable until at least one structured project entry exists; the system must clearly explain why if a student tries to access it without one.

## 8. AI Requirements

- Every LLM call goes through the AI abstraction layer described in `claude.md` / `plan.md` — no direct provider SDK calls from feature code.
- Resume field extraction (FR-9) and resume rewrite suggestions (FR-12) must include a validation step checking that AI output is grounded in the source resume text; ungrounded output must be rejected or flagged, not silently shown as fact.
- Recommendation phrasing (FR-31) may use an LLM only after deterministic ranking has already selected what to recommend.
- Project Defense question generation (FR-44) must construct questions from the structured project fields the student provided — the system must be able to show, for any generated question, which structured field(s) it's grounded in.
- Mentor responses (FR-37–39) must be groundable in the student's structured profile data plus the current conversation; no raw-history replay across sessions (FR-38).
- No feature may claim a specific model accuracy/performance number unless backed by real evaluation data (see claude.md AI/ML Principle 6).

## 9. ML Requirements

- No ML model is trained or deployed for readiness prediction in MVP (claude.md AI/ML Principle 3, 6).
- The system must log, from day one, the raw signals a future model would need: resume scores, assessment results, interview scores, roadmap completion patterns, and (when available) actual placement outcomes — the outcome field exists in the data model but is not populated or predicted in MVP; how it will eventually be collected is a documented open question, not a built feature.
- Any future ML work is out of MVP scope; this section exists so the data model doesn't foreclose it (see plan.md for the phased approach).

## 10. Database Requirements

See plan.md for full schema design. At minimum, the following entities are required for MVP (see claude.md for what's excluded): users, student_profiles, education, projects (structured), resumes, resume_analyses, skills (taxonomy), skill_aliases, student_skills, role_archetypes, role_archetype_skills, assessments, assessment_questions, assessment_attempts, assessment_answers, interviews, interview_questions, interview_answers, readiness_scores (historical), skill_gaps, recommendations, roadmap_tasks, memory_facts, notifications (optional for MVP — see tasks.md prioritization).

Non-negotiable data-model requirements:
- Field provenance tracking (FR-6).
- Roadmap task state must support skipped-by-student distinctly (FR-35).
- Readiness scores stored historically, not overwritten (FR-46, BR-2).
- Soft-delete support with grace-period timestamp on the account/user level (FR-4).

## 11. API Requirements

- RESTful API surface (see plan.md for exact structure), authenticated by default.
- Authorization: every endpoint scoped to the requesting student's own resources; no direct object reference across students.
- Rate limiting on all AI-calling endpoints.
- Endpoints must return explanation/breakdown data alongside any scored/ranked output (readiness, skill gaps, recommendations) — not just the headline number.

## 12. UI Requirements

- Dashboard as the primary landing view: current readiness score + explanation, top skill gaps, today's recommended actions.
- Every scored or AI-influenced output in the UI must have a visible "why" affordance (expandable explanation), consistent with claude.md's explainability principle.
- Resume suggestion review UI must present suggestions individually with clear Accept/Reject controls — no bulk "accept all."
- Roadmap UI must make skip/reorder/add/remove actions first-class, not buried.

## 13. Security & Privacy

See claude.md Security Principles and Privacy Principles — those apply in full and are not restated here to avoid drift between documents. Any security/privacy requirement introduced during implementation must be added to claude.md, not only to code comments.

## 14. Testing Requirements

- Unit tests for all deterministic scoring logic (readiness, skill gap, recommendation ranking) with fixed expected outputs — these are the highest-value tests given their explainability requirement.
- Validation tests specifically for AI-output grounding checks (FR-10, FR-12, FR-44) — e.g., a test asserting that a resume suggestion introducing an unsupported fact is rejected/flagged.
- Integration tests for the full core loop (profile → assessment → readiness → gap → recommendation → roadmap update).
- Auth/authorization tests confirming no cross-student data access.

## 15. Deployment Requirements

Single-environment, containerized, pragmatic cloud deployment (see plan.md). Not covered in MVP: multi-environment staging/prod split, full CI/CD pipelines, infrastructure-as-code, production-grade observability — these are documented as future infra maturity, not built now.

## 16. MVP Scope (Confirmed)

Per explicit product decision, MVP includes the full following set (none deferred):
- Student profile + structured project intake
- Resume: upload (PDF/DOCX) + parse + paste fallback; analysis + opt-in suggested rewrites
- Skill taxonomy + curated-bank assessments
- Rule-based, explainable readiness scoring
- Role-archetype job data (manually curated)
- Skill gap analysis
- Recommendation engine (rule-based ranking)
- Adaptive roadmap (student-overridable)
- AI Mentor (memory-facts based, bounded scope)
- Mock interview: text-only, general + project defense mode

## 17. Explicit Future Features (Not MVP)

- Voice-based mock interviews (STT/TTS)
- ML-based readiness prediction (once real outcome data exists)
- AI-generated assessment questions used for live grading (currently: curated bank only; AI-generated variants would need validation before being trusted)
- Live external job-listing integration / scraping
- Institutional/B2B: colleges, admin accounts, placement-officer/recruiter roles, multi-tenancy, cohort analytics
- Inactivity-based automatic data purging policy
- "Career Twin" — dropped; would need a genuinely distinct capability defined before ever being reconsidered

## 18. Assumptions

- No pre-existing labeled dataset of real placement outcomes exists at project start.
- The student population is assumed to have reasonable digital literacy (college students); no accessibility-for-low-literacy design requirement was raised.
- English-language resumes/interviews assumed for MVP (multilingual support not raised as a requirement).

## 19. Constraints

- Portfolio/B.Tech-project-scale build — architecture must be professional and scalable in principle but not overengineered (claude.md).
- No budget for paid job-listing APIs or paid resume-parsing vendors in MVP; LLM-based extraction via the existing AI abstraction layer is the parsing strategy (see plan.md and the research findings referenced there).

## 20. Acceptance Criteria (Product-Level)

The MVP is acceptance-complete when a single student can, without developer intervention:
1. Sign up, build a profile, add at least one structured project, and upload or paste a resume.
2. Receive a resume analysis with an explainable quality score and at least one opt-in suggested rewrite that does not introduce unsupported facts.
3. Select a target role archetype and see a skill-gap analysis against it.
4. Take at least one curated assessment and see their skill proficiency update.
5. See a readiness score with a visible factor breakdown that changes appropriately as the above signals change.
6. See ranked, explained recommendations and a roadmap they can accept/skip/reorder/edit.
7. Have a conversation with the AI mentor that references their actual profile data and results in at least one stored, student-visible, student-deletable memory fact.
8. Complete a general text mock interview and a project-defense mock interview (the latter grounded in their structured project fields), each producing scored, explained feedback that updates their profile/readiness signals.
