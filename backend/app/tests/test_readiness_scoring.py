import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import User, StudentProfile, Resume, ResumeAnalysis, StudentSkill, Skill, RoleArchetype, RoleArchetypeSkill
from app.modules.readiness.service import ReadinessScoringService

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_readiness_scoring_deterministic_formula(db_session):
    # Setup test user & profile
    user = User(email="teststudent@example.com", full_name="Test Student")
    db_session.add(user)
    db_session.flush()

    role = RoleArchetype(title="SDE-1 Backend", description="Backend SDE role")
    db_session.add(role)
    db_session.flush()

    profile = StudentProfile(user_id=user.id, target_role_id=role.id)
    db_session.add(profile)

    resume = Resume(user_id=user.id, file_type="paste", raw_text="Sample resume text")
    db_session.add(resume)
    db_session.flush()

    resume_analysis = ResumeAnalysis(
        resume_id=resume.id,
        overall_score=80.0,
        completeness_score=80.0,
        clarity_score=80.0,
        relevance_score=80.0
    )
    db_session.add(resume_analysis)

    skill = Skill(name="Python", category="Languages")
    db_session.add(skill)
    db_session.flush()

    db_session.add(RoleArchetypeSkill(role_archetype_id=role.id, skill_id=skill.id, is_essential=True, required_proficiency=80.0))
    db_session.add(StudentSkill(user_id=user.id, skill_id=skill.id, proficiency=80.0, confidence=1.0, source="assessment_verified"))
    db_session.commit()

    res = ReadinessScoringService.calculate_readiness(user.id, db_session)

    # Formula: 0.25*80 + 0.35*80 + 0.20*40 (default roadmap) + 0.20*30 (default interview)
    # = 20 + 28 + 8 + 6 = 62.0
    assert res["overall_score"] == 62.0
    assert "resume" in res["factor_breakdown"]
    assert res["factor_breakdown"]["resume"]["score"] == 80.0
    assert res["factor_breakdown"]["skills"]["score"] == 80.0
