from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models import (
    User, StudentProfile, Education, Project, StudentSkill, Resume,
    AssessmentAttempt, Interview, ReadinessScore, RoadmapTask, MemoryFact, Skill
)

router = APIRouter(prefix="/api/profile", tags=["profile"])

class ProfileUpdateSchema(BaseModel):
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    target_role_id: Optional[str] = None

class ProjectCreateSchema(BaseModel):
    name: str
    one_line_summary: str
    role: str
    tech_stack: List[str]
    architectural_decisions: str
    challenges_faced: str
    tradeoffs_made: str

@router.get("")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    education = db.query(Education).filter(Education.user_id == current_user.id).all()
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "branch": profile.branch if profile else None,
        "graduation_year": profile.graduation_year if profile else None,
        "target_role_id": profile.target_role_id if profile else None,
        "education": education,
        "projects": projects,
        "is_deleted": current_user.is_deleted,
        "deletion_requested_at": current_user.deletion_requested_at
    }

@router.put("")
def update_profile(payload: ProfileUpdateSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    if payload.branch is not None:
        profile.branch = payload.branch
    if payload.graduation_year is not None:
        profile.graduation_year = payload.graduation_year
    if payload.target_role_id is not None:
        profile.target_role_id = payload.target_role_id

    db.commit()
    return {"message": "Profile updated successfully"}

# Structured Project Intake Endpoints
@router.get("/projects")
def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.user_id == current_user.id).all()

@router.post("/projects")
def create_project(payload: ProjectCreateSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = Project(
        user_id=current_user.id,
        name=payload.name,
        one_line_summary=payload.one_line_summary,
        role=payload.role,
        tech_stack=payload.tech_stack,
        architectural_decisions=payload.architectural_decisions,
        challenges_faced=payload.challenges_faced,
        tradeoffs_made=payload.tradeoffs_made
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj

@router.delete("/projects/{project_id}")
def delete_project(project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    db.delete(proj)
    db.commit()
    return {"message": "Project deleted successfully"}

# Student Data Export (FR-3)
@router.get("/export")
def export_student_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    education = db.query(Education).filter(Education.user_id == current_user.id).all()
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    skills = db.query(StudentSkill).filter(StudentSkill.user_id == current_user.id).all()
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    attempts = db.query(AssessmentAttempt).filter(AssessmentAttempt.user_id == current_user.id).all()
    interviews = db.query(Interview).filter(Interview.user_id == current_user.id).all()
    scores = db.query(ReadinessScore).filter(ReadinessScore.user_id == current_user.id).all()
    memory_facts = db.query(MemoryFact).filter(MemoryFact.user_id == current_user.id).all()

    return {
        "export_date": datetime.utcnow().isoformat(),
        "user_info": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "branch": profile.branch if profile else None,
            "graduation_year": profile.graduation_year if profile else None
        },
        "education": [e.__dict__ for e in education],
        "projects": [p.__dict__ for p in projects],
        "skills": [s.__dict__ for s in skills],
        "resumes": [{"id": r.id, "file_name": r.file_name, "created_at": r.created_at} for r in resumes],
        "assessment_attempts": [a.__dict__ for a in attempts],
        "interviews": [i.__dict__ for i in interviews],
        "readiness_history": [r.__dict__ for r in scores],
        "memory_facts": [m.__dict__ for m in memory_facts]
    }

# Soft Delete Account & Grace Period (FR-4)
@router.post("/delete-account")
def request_account_deletion(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.is_deleted = True
    current_user.deletion_requested_at = datetime.utcnow()
    db.commit()
    
    expiry_date = current_user.deletion_requested_at + timedelta(days=settings.SOFT_DELETE_GRACE_PERIOD_DAYS)
    return {
        "message": f"Account soft-deleted. Permanent deletion scheduled on {expiry_date.strftime('%Y-%m-%d')}. You may cancel before this date by logging back in."
    }

@router.post("/cancel-deletion")
def cancel_account_deletion(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.is_deleted = False
    current_user.deletion_requested_at = None
    db.commit()
    return {"message": "Account deletion cancelled. Your account is fully restored."}
