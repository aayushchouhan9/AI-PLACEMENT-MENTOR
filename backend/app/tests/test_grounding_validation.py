import pytest
from app.modules.ai_abstraction.grounding_validator import GroundingValidator

def test_grounding_validator_accepts_valid_rewrite():
    source = "Developed backend REST APIs using Python and FastAPI. Increased request handling speed."
    suggested = "Developed robust backend REST APIs using Python and FastAPI, improving overall request handling speed."
    is_grounded, reasons = GroundingValidator.validate_resume_rewrite(source, suggested)
    assert is_grounded is True
    assert len(reasons) == 0

def test_grounding_validator_rejects_invented_metrics():
    source = "Optimized database query performance."
    suggested = "Optimized database query performance, achieving 99.9% uptime and 45% latency reduction."
    is_grounded, reasons = GroundingValidator.validate_resume_rewrite(source, suggested)
    assert is_grounded is False
    assert any("unsupported metrics" in r for r in reasons)

def test_grounding_validator_rejects_invented_technologies():
    source = "Built frontend user interfaces."
    suggested = "Built frontend user interfaces using Kubernetes and GraphQL."
    is_grounded, reasons = GroundingValidator.validate_resume_rewrite(source, suggested)
    assert is_grounded is False
    assert any("Kubernetes" in r or "GraphQL" in r for r in reasons)

def test_project_defense_question_grounding():
    project = {
        "name": "E-Commerce API",
        "role": "Backend Lead",
        "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
        "architectural_decisions": "Used modular monolithic structure with SQLAlchemy async ORM",
        "challenges_faced": "Handling concurrent database connections under high load",
        "tradeoffs_made": "Chose REST APIs over gRPC for simplicity"
    }
    valid_q = "How did you design the SQLAlchemy async connection pooling for E-Commerce API under high load?"
    is_grounded, reasons = GroundingValidator.validate_project_defense_question(project, valid_q)
    assert is_grounded is True

    unrelated_q = "Why did you choose Swift for iOS mobile development?"
    is_grounded, reasons = GroundingValidator.validate_project_defense_question(project, unrelated_q)
    assert is_grounded is False
