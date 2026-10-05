# AI Placement Mentor

AI Placement Mentor is a personal, continuously-learning placement-preparation mentor for college engineering students targeting tech-adjacent roles (SDE, Data, QA, Analyst).

## Closed Loop Vision

```
Profile + Resume + Projects → Skill Assessment → Readiness Analysis → Target Role →
Skill Gap Analysis → Recommendations → Adaptive Roadmap → Practice + Mock Interview →
Performance Analysis → Updated Profile → Updated Recommendations
```

## Source of Truth Documentation

- [`claude.md`](./claude.md) — Persistent project context, vision, philosophy, scope boundaries, AI/ML principles, security and privacy principles.
- [`spec.md`](./spec.md) — Product specifications, user journeys, functional requirements, and acceptance criteria.
- [`plan.md`](./plan.md) — Implementation architecture, modular monolith design, technology decisions, and database strategy.
- [`tasks.md`](./tasks.md) — Phased task breakdown and progress tracking.

## Architecture

- **Backend:** FastAPI (Python 3.11+), SQLAlchemy 2.0 async/sync ORM, Pydantic v2.
- **Frontend:** React SPA (Vite), Vanilla CSS dynamic theme.
- **Database:** PostgreSQL (with SQLite support for zero-config offline development).
- **AI Layer:** Internal provider-agnostic abstraction layer supporting Claude API & offline mock mode.

## Quick Start (Local Development)

### 1. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```
Backend API docs available at: http://localhost:8000/docs

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend Web App available at: http://localhost:5173

### 4. Docker Compose Setup (Optional)
```bash
docker-compose up --build
```
