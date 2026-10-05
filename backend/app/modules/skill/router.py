from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, Skill, StudentSkill

router = APIRouter(prefix="/api/skills", tags=["skills"])

class StudentSkillAddSchema(BaseModel):
    skill_id: str
    proficiency: float = 50.0

@router.get("")
def list_canonical_skills(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    return [{
        "id": s.id,
        "name": s.name,
        "category": s.category,
        "aliases": [a.alias_name for a in s.aliases]
    } for s in skills]

@router.get("/my-skills")
def get_my_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    my_skills = db.query(StudentSkill).filter(StudentSkill.user_id == current_user.id).all()
    return [{
        "id": ss.id,
        "skill_id": ss.skill_id,
        "name": ss.skill.name if ss.skill else "",
        "category": ss.skill.category if ss.skill else "",
        "proficiency": ss.proficiency,
        "confidence": ss.confidence,
        "source": ss.source,
        "updated_at": ss.updated_at
    } for ss in my_skills]

@router.post("/my-skills")
def declare_skill(payload: StudentSkillAddSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing = db.query(StudentSkill).filter(
        StudentSkill.user_id == current_user.id,
        StudentSkill.skill_id == payload.skill_id
    ).first()

    if existing:
        # Per Business Rule BR-1: assessment-verified > resume-extracted > self-declared
        if existing.source == "self_declared":
            existing.proficiency = payload.proficiency
            existing.confidence = 0.5
        db.commit()
        db.refresh(existing)
        return existing

    new_skill = StudentSkill(
        user_id=current_user.id,
        skill_id=payload.skill_id,
        proficiency=payload.proficiency,
        confidence=0.5,
        source="self_declared"
    )
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill
