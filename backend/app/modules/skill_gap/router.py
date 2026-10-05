from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, StudentProfile, RoleArchetype, RoleArchetypeSkill, StudentSkill, SkillGap

router = APIRouter(prefix="/api/skill-gaps", tags=["skill-gaps"])

@router.get("")
def get_skill_gaps(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile or not profile.target_role_id:
        return {
            "has_target_role": False,
            "message": "Select a target role to view detailed skill gaps.",
            "gaps": []
        }

    role = db.query(RoleArchetype).filter(RoleArchetype.id == profile.target_role_id).first()
    req_skills = db.query(RoleArchetypeSkill).filter(RoleArchetypeSkill.role_archetype_id == role.id).all()

    # Clear previous snapshot records for current target role
    db.query(SkillGap).filter(
        SkillGap.user_id == current_user.id,
        SkillGap.target_role_id == role.id
    ).delete()

    gaps_list = []
    for req in req_skills:
        st_skill = db.query(StudentSkill).filter(
            StudentSkill.user_id == current_user.id,
            StudentSkill.skill_id == req.skill_id
        ).first()

        current_prof = st_skill.proficiency if st_skill else 0.0
        gap_size = max(0.0, round(req.required_proficiency - current_prof, 1))

        if req.is_essential:
            priority_urgency = "high" if gap_size > 30 else ("medium" if gap_size > 0 else "low")
        else:
            priority_urgency = "medium" if gap_size > 40 else "low"

        explanation = f"Target role requires {req.required_proficiency}% proficiency in {req.skill.name if req.skill else ''}. Currently at {current_prof}%."
        if req.is_essential and gap_size > 20:
            explanation += " Critical essential skill gap for this position."

        gap_record = SkillGap(
            user_id=current_user.id,
            target_role_id=role.id,
            skill_id=req.skill_id,
            current_proficiency=current_prof,
            required_proficiency=req.required_proficiency,
            gap_size=gap_size,
            is_essential=req.is_essential,
            priority_urgency=priority_urgency,
            explanation_text=explanation
        )
        db.add(gap_record)
        gaps_list.append({
            "skill_id": req.skill_id,
            "skill_name": req.skill.name if req.skill else "",
            "category": req.skill.category if req.skill else "",
            "current_proficiency": current_prof,
            "required_proficiency": req.required_proficiency,
            "gap_size": gap_size,
            "is_essential": req.is_essential,
            "priority_urgency": priority_urgency,
            "explanation": explanation
        })

    db.commit()

    # Sort gaps by priority urgency (high -> medium -> low) and gap_size descending
    priority_order = {"high": 0, "medium": 1, "low": 2}
    gaps_list.sort(key=lambda x: (priority_order.get(x["priority_urgency"], 3), -x["gap_size"]))

    return {
        "has_target_role": True,
        "target_role_title": role.title,
        "gaps": gaps_list
    }
