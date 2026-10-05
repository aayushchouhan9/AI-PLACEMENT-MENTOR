import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

# User & Auth
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    full_name = Column(String(255), nullable=False)
    google_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    deletion_requested_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    student_skills = relationship("StudentSkill", back_populates="user", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="user", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    readiness_scores = relationship("ReadinessScore", back_populates="user", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    roadmap_tasks = relationship("RoadmapTask", back_populates="user", cascade="all, delete-orphan")
    memory_facts = relationship("MemoryFact", back_populates="user", cascade="all, delete-orphan")


# Student Profile
class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    branch = Column(String(100), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    target_role_id = Column(String(36), ForeignKey("role_archetypes.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")
    target_role = relationship("RoleArchetype")


# Education
class Education(Base):
    __tablename__ = "education"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(100), nullable=False)
    field_of_study = Column(String(100), nullable=True)
    start_year = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    grade = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="education")


# Structured Project Intake
class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    one_line_summary = Column(Text, nullable=False)
    role = Column(String(255), nullable=False)
    tech_stack = Column(JSON, nullable=False, default=list)  # List of skill strings
    architectural_decisions = Column(Text, nullable=False)
    challenges_faced = Column(Text, nullable=False)
    tradeoffs_made = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="projects")


# Skill Taxonomy & Student Skills
class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False)  # Core CS, Languages, Frameworks, Tools, Soft Skills

    aliases = relationship("SkillAlias", back_populates="skill", cascade="all, delete-orphan")


class SkillAlias(Base):
    __tablename__ = "skill_aliases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    alias_name = Column(String(100), unique=True, index=True, nullable=False)

    skill = relationship("Skill", back_populates="aliases")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    proficiency = Column(Float, default=50.0)  # 0.0 to 100.0
    confidence = Column(Float, default=0.5)     # 0.0 to 1.0
    source = Column(String(50), nullable=False) # self_declared, resume_extracted, assessment_verified
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="student_skills")
    skill = relationship("Skill")


# Role Archetypes
class RoleArchetype(Base):
    __tablename__ = "role_archetypes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    typical_experience_level = Column(String(50), default="Entry-Level / Graduate")
    created_at = Column(DateTime, default=datetime.utcnow)

    skills = relationship("RoleArchetypeSkill", back_populates="role_archetype", cascade="all, delete-orphan")


class RoleArchetypeSkill(Base):
    __tablename__ = "role_archetype_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    role_archetype_id = Column(String(36), ForeignKey("role_archetypes.id"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    is_essential = Column(Boolean, default=True)
    required_proficiency = Column(Float, default=70.0)

    role_archetype = relationship("RoleArchetype", back_populates="skills")
    skill = relationship("Skill")


# Resumes
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_type = Column(String(50), nullable=False)  # pdf, docx, paste
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")
    analysis = relationship("ResumeAnalysis", back_populates="resume", uselist=False, cascade="all, delete-orphan")


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_id = Column(String(36), ForeignKey("resumes.id"), unique=True, nullable=False)
    overall_score = Column(Float, nullable=False)
    completeness_score = Column(Float, nullable=False)
    clarity_score = Column(Float, nullable=False)
    relevance_score = Column(Float, nullable=False)
    factor_breakdown = Column(JSON, nullable=False, default=dict)
    extracted_data = Column(JSON, nullable=False, default=dict)
    suggested_rewrites = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="analysis")


# Assessment Engine
class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    difficulty_tier = Column(String(50), nullable=False)  # beginner, intermediate, advanced
    time_limit_minutes = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)

    skill = relationship("Skill")
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    attempts = relationship("AssessmentAttempt", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="mcq")  # mcq, code_snippet
    options = Column(JSON, nullable=False, default=list)  # List of option strings
    correct_answer = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    points = Column(Integer, default=10)

    assessment = relationship("Assessment", back_populates="questions")
    skill = relationship("Skill")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False)
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    time_taken_seconds = Column(Integer, default=0)
    status = Column(String(50), default="completed")  # in_progress, completed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="assessment_attempts")
    assessment = relationship("Assessment", back_populates="attempts")
    answers = relationship("AssessmentAnswer", back_populates="attempt", cascade="all, delete-orphan")


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("assessment_attempts.id"), nullable=False)
    question_id = Column(String(36), ForeignKey("assessment_questions.id"), nullable=False)
    selected_option = Column(String(255), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    points_awarded = Column(Integer, default=0)

    attempt = relationship("AssessmentAttempt", back_populates="answers")
    question = relationship("AssessmentQuestion")


# Mock Interviews
class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    interview_type = Column(String(50), nullable=False)  # general, project_defense
    target_role_id = Column(String(36), ForeignKey("role_archetypes.id"), nullable=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    status = Column(String(50), default="completed")  # in_progress, completed
    overall_score = Column(Float, default=0.0)
    summary_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="interviews")
    target_role = relationship("RoleArchetype")
    project = relationship("Project")
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    interview_id = Column(String(36), ForeignKey("interviews.id"), nullable=False)
    question_order = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    grounded_project_fields = Column(JSON, nullable=True)  # References structured project fields if project_defense
    question_category = Column(String(50), default="technical")

    interview = relationship("Interview", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("interview_questions.id"), unique=True, nullable=False)
    user_answer_text = Column(Text, nullable=False)
    score = Column(Float, default=0.0)
    feedback_text = Column(Text, nullable=False)
    strengths = Column(JSON, nullable=False, default=list)
    improvements = Column(JSON, nullable=False, default=list)
    answered_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("InterviewQuestion", back_populates="answer")


# Placement Readiness Score (Historical)
class ReadinessScore(Base):
    __tablename__ = "readiness_scores"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    target_role_id = Column(String(36), ForeignKey("role_archetypes.id"), nullable=True)
    overall_score = Column(Float, nullable=False)
    resume_score_contrib = Column(Float, nullable=False)
    skill_score_contrib = Column(Float, nullable=False)
    roadmap_score_contrib = Column(Float, nullable=False)
    interview_score_contrib = Column(Float, nullable=False)
    factor_breakdown = Column(JSON, nullable=False, default=dict)
    formula_version = Column(String(20), default="1.0.0")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="readiness_scores")
    target_role = relationship("RoleArchetype")


# Skill Gaps & Recommendations
class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    target_role_id = Column(String(36), ForeignKey("role_archetypes.id"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    current_proficiency = Column(Float, default=0.0)
    required_proficiency = Column(Float, nullable=False)
    gap_size = Column(Float, nullable=False)
    is_essential = Column(Boolean, default=True)
    priority_urgency = Column(String(50), nullable=False)  # high, medium, low
    explanation_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="skill_gaps")
    target_role = relationship("RoleArchetype")
    skill = relationship("Skill")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    target_role_id = Column(String(36), ForeignKey("role_archetypes.id"), nullable=True)
    action_type = Column(String(50), nullable=False)  # take_assessment, study_topic, mock_interview, resume_improvement
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    phrased_description = Column(Text, nullable=True)
    reasoning_payload = Column(JSON, nullable=False, default=dict)
    priority_score = Column(Float, default=0.0)
    status = Column(String(50), default="active")  # active, actioned, dismissed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")


# Adaptive Roadmap Tasks
class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    recommendation_id = Column(String(36), ForeignKey("recommendations.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    task_type = Column(String(50), nullable=False)
    priority = Column(String(50), default="medium")
    status = Column(String(50), default="pending")  # pending, in_progress, completed, skipped_by_student
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="roadmap_tasks")
    recommendation = relationship("Recommendation")


# Memory Facts
class MemoryFact(Base):
    __tablename__ = "memory_facts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    fact_text = Column(Text, nullable=False)
    category = Column(String(50), default="general")  # skill_struggle, role_preference, learning_style
    source_conversation_ref = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memory_facts")
