from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, StudentProfile, MemoryFact, Project, StudentSkill
from app.modules.ai_abstraction.service import ai_service

router = APIRouter(prefix="/api/mentor", tags=["mentor"])

class ChatMessageSchema(BaseModel):
    message: str

@router.post("/chat")
def chat_with_mentor(payload: ChatMessageSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    memory_facts = db.query(MemoryFact).filter(MemoryFact.user_id == current_user.id).all()
    skills = db.query(StudentSkill).filter(StudentSkill.user_id == current_user.id).all()
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()

    # Profile context string (bounded context, no raw conversation replay)
    profile_ctx = {
        "full_name": current_user.full_name,
        "target_role": profile.target_role.title if profile and profile.target_role else "Tech-Adjacent Engineering",
        "verified_skills": [s.skill.name for s in skills if s.source == "assessment_verified"],
        "stored_memory_facts": [m.fact_text for m in memory_facts],
        "project_count": len(projects)
    }

    # Complete mentor interaction via AI Abstraction Layer
    response = ai_service.complete("mentor_conversation", {
        "message": payload.message,
        "profile": profile_ctx
    }, user_id=current_user.id)

    # Extract memory facts from turn
    fact_res = ai_service.complete("memory_fact_extraction", {
        "user_message": payload.message,
        "ai_reply": response.get("reply", "")
    }, user_id=current_user.id)

    new_fact_objects = []
    for fact in fact_res.get("facts", []):
        fact_rec = MemoryFact(
            user_id=current_user.id,
            fact_text=fact.get("fact_text", ""),
            category=fact.get("category", "general"),
            source_conversation_ref="mentor_chat"
        )
        db.add(fact_rec)
        new_fact_objects.append(fact.get("fact_text"))

    db.commit()

    return {
        "reply": response.get("reply", ""),
        "extracted_facts": new_fact_objects
    }

@router.get("/memory-facts")
def get_memory_facts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    facts = db.query(MemoryFact).filter(MemoryFact.user_id == current_user.id).all()
    return [{
        "id": f.id,
        "fact_text": f.fact_text,
        "category": f.category,
        "created_at": f.created_at
    } for f in facts]

@router.delete("/memory-facts/{fact_id}")
def delete_memory_fact(fact_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fact = db.query(MemoryFact).filter(MemoryFact.id == fact_id, MemoryFact.user_id == current_user.id).first()
    if not fact:
        raise HTTPException(status_code=404, detail="Memory fact not found")
    db.delete(fact)
    db.commit()
    return {"message": "Memory fact deleted successfully"}
