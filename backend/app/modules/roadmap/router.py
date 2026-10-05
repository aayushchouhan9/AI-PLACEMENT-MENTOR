from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, RoadmapTask, Recommendation

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])

class RoadmapTaskCreateSchema(BaseModel):
    title: str
    description: str
    task_type: str = "custom"
    priority: str = "medium"

class RoadmapTaskUpdateSchema(BaseModel):
    status: Optional[str] = None  # pending, in_progress, completed, skipped_by_student
    priority: Optional[str] = None

@router.get("")
def get_roadmap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(RoadmapTask).filter(RoadmapTask.user_id == current_user.id).order_by(RoadmapTask.created_at.desc()).all()
    return [{
        "id": t.id,
        "recommendation_id": t.recommendation_id,
        "title": t.title,
        "description": t.description,
        "task_type": t.task_type,
        "priority": t.priority,
        "status": t.status,  # pending, in_progress, completed, skipped_by_student
        "updated_at": t.updated_at
    } for t in tasks]

@router.post("/generate")
def generate_roadmap_from_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    active_recs = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.status == "active"
    ).all()

    existing_tasks = db.query(RoadmapTask).filter(RoadmapTask.user_id == current_user.id).all()
    existing_titles = {t.title for t in existing_tasks}

    new_tasks = []
    for rec in active_recs:
        if rec.title not in existing_titles:
            task = RoadmapTask(
                user_id=current_user.id,
                recommendation_id=rec.id,
                title=rec.title,
                description=rec.phrased_description or rec.description,
                task_type=rec.action_type,
                priority="high" if rec.priority_score > 80 else "medium",
                status="pending"
            )
            db.add(task)
            new_tasks.append(rec.title)

    db.commit()
    return {
        "message": f"Roadmap updated. Added {len(new_tasks)} new task(s). Preserved existing student overrides.",
        "added_tasks": new_tasks
    }

@router.post("/tasks")
def add_custom_task(payload: RoadmapTaskCreateSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = RoadmapTask(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        task_type=payload.task_type,
        priority=payload.priority,
        status="pending"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.put("/tasks/{task_id}")
def update_roadmap_task(
    task_id: str,
    payload: RoadmapTaskUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(RoadmapTask).filter(RoadmapTask.id == task_id, RoadmapTask.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Roadmap task not found")

    if payload.status is not None:
        valid_statuses = ["pending", "in_progress", "completed", "skipped_by_student"]
        if payload.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
        task.status = payload.status

    if payload.priority is not None:
        task.priority = payload.priority

    db.commit()
    db.refresh(task)
    return {
        "message": f"Task state updated to '{task.status}'",
        "task_id": task.id,
        "status": task.status
    }

@router.delete("/tasks/{task_id}")
def delete_roadmap_task(task_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(RoadmapTask).filter(RoadmapTask.id == task_id, RoadmapTask.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Roadmap task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task removed from roadmap"}
