from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import (
    User, Assessment, AssessmentQuestion, AssessmentAttempt,
    AssessmentAnswer, StudentSkill
)

router = APIRouter(prefix="/api/assessments", tags=["assessments"])

class SubmitAnswerSchema(BaseModel):
    question_id: str
    selected_option: str

class SubmitAssessmentSchema(BaseModel):
    answers: List[SubmitAnswerSchema]
    time_taken_seconds: int = 120

@router.get("")
def list_assessments(db: Session = Depends(get_db)):
    assessments = db.query(Assessment).all()
    return [{
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "skill_name": a.skill.name if a.skill else "",
        "difficulty_tier": a.difficulty_tier,
        "time_limit_minutes": a.time_limit_minutes,
        "question_count": len(a.questions)
    } for a in assessments]

@router.get("/{assessment_id}")
def get_assessment_details(assessment_id: str, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    questions = [{
        "id": q.id,
        "question_text": q.question_text,
        "question_type": q.question_type,
        "options": q.options,
        "points": q.points
    } for q in assessment.questions]

    return {
        "id": assessment.id,
        "title": assessment.title,
        "description": assessment.description,
        "skill_name": assessment.skill.name if assessment.skill else "",
        "difficulty_tier": assessment.difficulty_tier,
        "time_limit_minutes": assessment.time_limit_minutes,
        "questions": questions
    }

@router.post("/{assessment_id}/submit")
def submit_assessment(
    assessment_id: str,
    payload: SubmitAssessmentSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    questions_map = {q.id: q for q in assessment.questions}
    total_score = 0.0
    max_score = sum(q.points for q in assessment.questions) or 10.0

    attempt = AssessmentAttempt(
        user_id=current_user.id,
        assessment_id=assessment.id,
        status="completed",
        time_taken_seconds=payload.time_taken_seconds,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    db.add(attempt)
    db.flush()

    answer_results = []
    for user_ans in payload.answers:
        q_obj = questions_map.get(user_ans.question_id)
        if not q_obj:
            continue
        
        is_correct = (user_ans.selected_option.strip() == q_obj.correct_answer.strip())
        points = q_obj.points if is_correct else 0
        total_score += points

        ans_record = AssessmentAnswer(
            attempt_id=attempt.id,
            question_id=q_obj.id,
            selected_option=user_ans.selected_option,
            is_correct=is_correct,
            points_awarded=points
        )
        db.add(ans_record)
        answer_results.append({
            "question_id": q_obj.id,
            "question_text": q_obj.question_text,
            "selected_option": user_ans.selected_option,
            "correct_answer": q_obj.correct_answer,
            "is_correct": is_correct,
            "explanation": q_obj.explanation
        })

    percentage = round((total_score / max_score) * 100.0, 1)
    attempt.score = total_score
    attempt.max_score = max_score
    attempt.percentage = percentage

    # Update StudentSkill record: Upgrade source to assessment_verified and confidence to 1.0 (BR-1, FR-20)
    student_skill = db.query(StudentSkill).filter(
        StudentSkill.user_id == current_user.id,
        StudentSkill.skill_id == assessment.skill_id
    ).first()

    if not student_skill:
        student_skill = StudentSkill(
            user_id=current_user.id,
            skill_id=assessment.skill_id,
            proficiency=percentage,
            confidence=1.0,
            source="assessment_verified"
        )
        db.add(student_skill)
    else:
        student_skill.proficiency = max(student_skill.proficiency, percentage)
        student_skill.confidence = 1.0
        student_skill.source = "assessment_verified"

    db.commit()

    return {
        "attempt_id": attempt.id,
        "score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "answers": answer_results,
        "skill_updated": {
            "skill_name": assessment.skill.name if assessment.skill else "",
            "new_proficiency": student_skill.proficiency,
            "provenance": student_skill.source
        }
    }
