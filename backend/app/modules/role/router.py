from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, RoleArchetype, RoleArchetypeSkill, StudentProfile

router = APIRouter(prefix="/api/roles", tags=["roles"])

class SelectRoleSchema(BaseModel):
    role_id: str

@router.get("")
def list_role_archetypes(db: Session = Depends(get_db)):
    roles = db.query(RoleArchetype).all()
    return [{
        "id": r.id,
        "title": r.title,
        "description": r.description,
        "typical_experience_level": r.typical_experience_level,
        "skill_count": len(r.skills)
    } for r in roles]

@router.get("/{role_id}")
def get_role_archetype_details(role_id: str, db: Session = Depends(get_db)):
    role = db.query(RoleArchetype).filter(RoleArchetype.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role archetype not found")

    skills = [{
        "skill_id": rs.skill_id,
        "name": rs.skill.name if rs.skill else "",
        "category": rs.skill.category if rs.skill else "",
        "is_essential": rs.is_essential,
        "required_proficiency": rs.required_proficiency
    } for rs in role.skills]

    return {
        "id": role.id,
        "title": role.title,
        "description": role.description,
        "typical_experience_level": role.typical_experience_level,
        "required_skills": skills
    }

@router.post("/select")
def select_target_role(payload: SelectRoleSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role = db.query(RoleArchetype).filter(RoleArchetype.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role archetype not found")

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    profile.target_role_id = role.id
    db.commit()

    return {
        "message": f"Target role set to {role.title}",
        "target_role_id": role.id,
        "target_role_title": role.title
    }
