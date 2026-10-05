from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.modules.auth.router import router as auth_router
from app.modules.profile.router import router as profile_router
from app.modules.resume.router import router as resume_router
from app.modules.skill.router import router as skill_router
from app.modules.assessment.router import router as assessment_router
from app.modules.readiness.router import router as readiness_router
from app.modules.role.router import router as role_router
from app.modules.skill_gap.router import router as skill_gap_router
from app.modules.recommendation.router import router as recommendation_router
from app.modules.roadmap.router import router as roadmap_router
from app.modules.mentor.router import router as mentor_router
from app.modules.interview.router import router as interview_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Placement Mentor - Personal continuously-learning mentor for college engineering students"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    from app.core.database import engine, Base, SessionLocal
    from app.seed.seed_data import seed_database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

# Include all 13 module routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(resume_router)
app.include_router(skill_router)
app.include_router(assessment_router)
app.include_router(readiness_router)
app.include_router(role_router)
app.include_router(skill_gap_router)
app.include_router(recommendation_router)
app.include_router(roadmap_router)
app.include_router(mentor_router)
app.include_router(interview_router)

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
