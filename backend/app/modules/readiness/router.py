from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, ReadinessScore
from app.modules.readiness.service import ReadinessScoringService

router = APIRouter(prefix="/api/readiness", tags=["readiness"])

@router.get("")
def get_current_readiness_score(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ReadinessScoringService.calculate_readiness(current_user.id, db)

@router.get("/history")
def get_readiness_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = db.query(ReadinessScore).filter(
        ReadinessScore.user_id == current_user.id
    ).order_by(ReadinessScore.created_at.asc()).all()

    return [{
        "id": h.id,
        "overall_score": h.overall_score,
        "resume": h.resume_score_contrib,
        "skills": h.skill_score_contrib,
        "roadmap": h.roadmap_score_contrib,
        "interview": h.interview_score_contrib,
        "created_at": h.created_at
    } for h in history]
