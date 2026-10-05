from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, SkillGap, Recommendation, Resume, Project, Assessment
from app.modules.ai_abstraction.service import ai_service

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.get("")
def get_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Fetch current top skill gaps
    gaps = db.query(SkillGap).filter(SkillGap.user_id == current_user.id).all()
    
    # 2. Rule-based recommendation ranking engine
    recs_to_create = []

    # Check resume upload state
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        recs_to_create.append({
            "action_type": "resume_improvement",
            "title": "Upload or Paste Your Resume",
            "description": "Upload a PDF/DOCX resume or paste raw text to receive resume quality analysis and keyword extraction.",
            "priority_score": 95.0,
            "reasoning": "Resume input is required to evaluate resume quality score in readiness formula."
        })

    # Check structured project intake state
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    if not projects:
        recs_to_create.append({
            "action_type": "study_topic",
            "title": "Add a Structured Project Entry",
            "description": "Log your project architecture, tech stack, and trade-offs to unlock Project Defense Mock Interview mode.",
            "priority_score": 90.0,
            "reasoning": "Project Defense mode requires at least one structured project entry."
        })

    # Generate assessment & study recommendations from top skill gaps
    for gap in gaps:
        if gap.gap_size > 0:
            assessment = db.query(Assessment).filter(Assessment.skill_id == gap.skill_id).first()
            skill_name = gap.skill.name if gap.skill else "this skill"
            
            p_score = 80.0 if gap.priority_urgency == "high" else 60.0
            p_score += (gap.gap_size * 0.2)

            if assessment:
                recs_to_create.append({
                    "action_type": "take_assessment",
                    "title": f"Take Assessment: {assessment.title}",
                    "description": f"Complete the {assessment.difficulty_tier} assessment for {skill_name} to verify your proficiency.",
                    "priority_score": round(p_score, 1),
                    "reasoning": f"Current proficiency is {gap.current_proficiency}%, required is {gap.required_proficiency}%."
                })
            else:
                recs_to_create.append({
                    "action_type": "study_topic",
                    "title": f"Study Topic: {skill_name}",
                    "description": f"Review key concepts and complete practice problems in {skill_name} to close your skill gap.",
                    "priority_score": round(p_score - 5.0, 1),
                    "reasoning": f"Essential skill gap of {gap.gap_size}% identified for target role."
                })

    # Add mock interview recommendation
    recs_to_create.append({
        "action_type": "mock_interview",
        "title": "Attempt a General Mock Interview",
        "description": "Practice answering technical and behavioral interview questions under timed simulation.",
        "priority_score": 75.0,
        "reasoning": "Mock interview sessions contribute 20% to your overall placement readiness score."
    })

    # Sort deterministically by priority_score descending
    recs_to_create.sort(key=lambda r: r["priority_score"], reverse=True)

    # Save to Recommendations table and phrase descriptions using AI Abstraction Layer
    db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.status == "active"
    ).delete()

    output_recs = []
    for rec in recs_to_create[:5]:  # Top 5 ranked recommendations
        phrased = ai_service.complete("recommendation_phrasing", {
            "title": rec["title"],
            "description": rec["description"]
        }, user_id=current_user.id)

        rec_db = Recommendation(
            user_id=current_user.id,
            action_type=rec["action_type"],
            title=rec["title"],
            description=rec["description"],
            phrased_description=phrased.get("phrased_description", rec["description"]),
            reasoning_payload={"reasoning": rec["reasoning"], "priority_score": rec["priority_score"]},
            priority_score=rec["priority_score"],
            status="active"
        )
        db.add(rec_db)
        db.flush()

        output_recs.append({
            "id": rec_db.id,
            "action_type": rec_db.action_type,
            "title": rec_db.title,
            "description": rec_db.description,
            "phrased_description": rec_db.phrased_description,
            "priority_score": rec_db.priority_score,
            "reasoning": rec["reasoning"]
        })

    db.commit()
    return output_recs
