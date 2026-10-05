from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import (
    User, StudentProfile, Project, Interview, InterviewQuestion, InterviewAnswer
)
from app.modules.ai_abstraction.service import ai_service
from app.modules.ai_abstraction.grounding_validator import GroundingValidator

router = APIRouter(prefix="/api/interviews", tags=["interviews"])

class StartInterviewSchema(BaseModel):
    interview_type: str  # 'general' or 'project_defense'
    project_id: Optional[str] = None

class SubmitInterviewAnswerSchema(BaseModel):
    question_id: str
    answer_text: str

GENERAL_QUESTIONS_BANK = [
    {"text": "Explain the difference between a process and a thread. How do they share memory?", "category": "technical"},
    {"text": "Describe a scenario where you had to debug a difficult software defect. What steps did you take?", "category": "behavioral"},
    {"text": "How do indexing and transactions ensure performance and consistency in relational databases?", "category": "technical"}
]

@router.post("/start")
def start_interview(payload: StartInterviewSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()

    # Precondition check for Project Defense Mode (BR-5, FR-43)
    if payload.interview_type == "project_defense":
        user_projects = db.query(Project).filter(Project.user_id == current_user.id).all()
        if not user_projects:
            raise HTTPException(
                status_code=400,
                detail="Project Defense Mode is unavailable until at least one structured project entry exists. Please add a project in your profile first."
            )
        
        target_project = None
        if payload.project_id:
            target_project = db.query(Project).filter(Project.id == payload.project_id, Project.user_id == current_user.id).first()
        if not target_project:
            target_project = user_projects[0]

        interview = Interview(
            user_id=current_user.id,
            interview_type="project_defense",
            target_role_id=profile.target_role_id if profile else None,
            project_id=target_project.id,
            status="in_progress"
        )
        db.add(interview)
        db.flush()

        # Generate template/rule-grounded project defense questions
        ai_res = ai_service.complete("project_defense_question_gen", {
            "project": {
                "name": target_project.name,
                "role": target_project.role,
                "tech_stack": target_project.tech_stack,
                "architectural_decisions": target_project.architectural_decisions,
                "challenges_faced": target_project.challenges_faced,
                "tradeoffs_made": target_project.tradeoffs_made
            }
        }, user_id=current_user.id)

        q1 = InterviewQuestion(
            interview_id=interview.id,
            question_order=1,
            question_text=ai_res.get("question_text"),
            grounded_project_fields=ai_res.get("grounded_fields", ["architectural_decisions"]),
            question_category="project_defense"
        )
        q2 = InterviewQuestion(
            interview_id=interview.id,
            question_order=2,
            question_text=f"In your '{target_project.name}' project, what was the biggest technical challenge faced ({target_project.challenges_faced[:60]}...) and how did you resolve it?",
            grounded_project_fields=["challenges_faced"],
            question_category="project_defense"
        )
        db.add_all([q1, q2])

    else:
        # General Mock Interview Mode
        interview = Interview(
            user_id=current_user.id,
            interview_type="general",
            target_role_id=profile.target_role_id if profile else None,
            status="in_progress"
        )
        db.add(interview)
        db.flush()

        for idx, q_data in enumerate(GENERAL_QUESTIONS_BANK, start=1):
            q_obj = InterviewQuestion(
                interview_id=interview.id,
                question_order=idx,
                question_text=q_data["text"],
                question_category=q_data["category"]
            )
            db.add(q_obj)

    db.commit()

    questions = db.query(InterviewQuestion).filter(InterviewQuestion.interview_id == interview.id).order_by(InterviewQuestion.question_order.asc()).all()

    return {
        "interview_id": interview.id,
        "interview_type": interview.interview_type,
        "project_id": interview.project_id,
        "questions": [{
            "id": q.id,
            "order": q.question_order,
            "text": q.question_text,
            "category": q.question_category,
            "grounded_project_fields": q.grounded_project_fields
        } for q in questions]
    }

@router.post("/{interview_id}/answer")
def submit_answer(
    interview_id: str,
    payload: SubmitInterviewAnswerSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found")

    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == payload.question_id,
        InterviewQuestion.interview_id == interview.id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found in interview")

    # Evaluate answer via AI Abstraction Layer
    ai_eval = ai_service.complete("mock_interview_feedback", {
        "question_text": question.question_text,
        "answer_text": payload.answer_text
    }, user_id=current_user.id)

    ans_record = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == question.id).first()
    if not ans_record:
        ans_record = InterviewAnswer(
            question_id=question.id,
            user_answer_text=payload.answer_text,
            score=ai_eval.get("score", 70.0),
            feedback_text=ai_eval.get("feedback_text", "Good response."),
            strengths=ai_eval.get("strengths", []),
            improvements=ai_eval.get("improvements", [])
        )
        db.add(ans_record)
    else:
        ans_record.user_answer_text = payload.answer_text
        ans_record.score = ai_eval.get("score", 70.0)
        ans_record.feedback_text = ai_eval.get("feedback_text", "Good response.")
        ans_record.strengths = ai_eval.get("strengths", [])
        ans_record.improvements = ai_eval.get("improvements", [])

    db.commit()

    return {
        "question_id": question.id,
        "score": ans_record.score,
        "feedback_text": ans_record.feedback_text,
        "strengths": ans_record.strengths,
        "improvements": ans_record.improvements
    }

@router.post("/{interview_id}/complete")
def complete_interview(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found")

    questions = db.query(InterviewQuestion).filter(InterviewQuestion.interview_id == interview.id).all()
    scores = []
    for q in questions:
        if q.answer:
            scores.append(q.answer.score)

    overall_score = round(sum(scores) / len(scores), 1) if scores else 50.0
    interview.status = "completed"
    interview.overall_score = overall_score
    interview.summary_feedback = f"Completed mock interview session with an overall performance score of {overall_score}/100."
    interview.completed_at = datetime.utcnow()

    db.commit()

    return {
        "interview_id": interview.id,
        "overall_score": overall_score,
        "summary_feedback": interview.summary_feedback,
        "completed_at": interview.completed_at
    }

@router.get("/history")
def get_interview_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interviews = db.query(Interview).filter(Interview.user_id == current_user.id).order_by(Interview.created_at.desc()).all()
    return [{
        "id": i.id,
        "type": i.interview_type,
        "status": i.status,
        "overall_score": i.overall_score,
        "summary_feedback": i.summary_feedback,
        "created_at": i.created_at
    } for i in interviews]
