import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import User, StudentProfile, Project, Resume, Skill, RoleArchetype, RoleArchetypeSkill, StudentSkill
from app.modules.readiness.service import ReadinessScoringService

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_full_closed_loop_readiness(db_session):
    # 1. Sign up student user
    user = User(email="e2e_student@example.com", full_name="E2E Student")
    db_session.add(user)
    db_session.flush()

    profile = StudentProfile(user_id=user.id)
    db_session.add(profile)

    # Initial readiness score
    r0 = ReadinessScoringService.calculate_readiness(user.id, db_session)
    assert r0["overall_score"] < 40.0  # Initial low confidence readiness score

    # 2. Add structured project
    proj = Project(
        user_id=user.id,
        name="Microservices Backend",
        one_line_summary="High-performance backend API",
        role="Lead Architect",
        tech_stack=["Python", "FastAPI"],
        architectural_decisions="Used async event loops",
        challenges_faced="Handling high concurrency",
        tradeoffs_made="Prioritized throughput over memory footprint"
    )
    db_session.add(proj)

    # 3. Add skill assessment result
    sk = Skill(name="Python", category="Languages")
    db_session.add(sk)
    db_session.flush()

    role = RoleArchetype(title="SDE-1 Backend", description="Backend SDE")
    db_session.add(role)
    db_session.flush()

    db_session.add(RoleArchetypeSkill(role_archetype_id=role.id, skill_id=sk.id, is_essential=True, required_proficiency=80.0))
    profile.target_role_id = role.id

    db_session.add(StudentSkill(user_id=user.id, skill_id=sk.id, proficiency=90.0, confidence=1.0, source="assessment_verified"))
    db_session.commit()

    # Updated readiness score
    r1 = ReadinessScoringService.calculate_readiness(user.id, db_session)
    assert r1["overall_score"] > r0["overall_score"]
    assert r1["factor_breakdown"]["skills"]["score"] == 90.0
