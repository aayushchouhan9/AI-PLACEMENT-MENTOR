from sqlalchemy.orm import Session
from app.models import (
    User, StudentProfile, Resume, ResumeAnalysis, StudentSkill,
    RoleArchetype, RoleArchetypeSkill, RoadmapTask, Interview, ReadinessScore
)

class ReadinessScoringService:
    FORMULA_VERSION = "1.0.0"

    @classmethod
    def calculate_readiness(cls, user_id: str, db: Session) -> dict:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        target_role_id = profile.target_role_id if profile else None
        target_role = db.query(RoleArchetype).filter(RoleArchetype.id == target_role_id).first() if target_role_id else None

        # 1. Resume Score (Weight: 0.25)
        latest_resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).first()
        if latest_resume and latest_resume.analysis:
            s_resume = latest_resume.analysis.overall_score
            resume_reason = f"Based on analyzed resume '{latest_resume.file_name}'"
        else:
            s_resume = 35.0
            resume_reason = "No resume uploaded yet (default partial score)"

        # 2. Skill Score (Weight: 0.35)
        if target_role:
            req_skills = db.query(RoleArchetypeSkill).filter(RoleArchetypeSkill.role_archetype_id == target_role.id).all()
            total_weighted_prof = 0.0
            total_req = len(req_skills) or 1
            for req in req_skills:
                st_skill = db.query(StudentSkill).filter(
                    StudentSkill.user_id == user_id,
                    StudentSkill.skill_id == req.skill_id
                ).first()
                if st_skill:
                    total_weighted_prof += (st_skill.proficiency * st_skill.confidence)
            s_skill = min(100.0, round(total_weighted_prof / total_req, 1))
            skill_reason = f"Evaluated against essential skills for {target_role.title}"
        else:
            all_st_skills = db.query(StudentSkill).filter(StudentSkill.user_id == user_id).all()
            if all_st_skills:
                s_skill = round(sum(s.proficiency * s.confidence for s in all_st_skills) / len(all_st_skills), 1)
                skill_reason = "General skill proficiency (no target role selected)"
            else:
                s_skill = 25.0
                skill_reason = "No skill assessments completed yet (role-agnostic fallback)"

        # 3. Roadmap Score (Weight: 0.20)
        tasks = db.query(RoadmapTask).filter(RoadmapTask.user_id == user_id).all()
        if tasks:
            completed_count = sum(1 for t in tasks if t.status == "completed")
            s_roadmap = round((completed_count / len(tasks)) * 100.0, 1)
            roadmap_reason = f"{completed_count}/{len(tasks)} roadmap tasks completed"
        else:
            s_roadmap = 40.0
            roadmap_reason = "No active roadmap tasks actioned"

        # 4. Mock Interview Score (Weight: 0.20)
        interviews = db.query(Interview).filter(Interview.user_id == user_id, Interview.status == "completed").all()
        if interviews:
            s_interview = round(sum(i.overall_score for i in interviews) / len(interviews), 1)
            interview_reason = f"Average score across {len(interviews)} completed mock interview session(s)"
        else:
            s_interview = 30.0
            interview_reason = "No mock interview sessions completed yet"

        # Formula calculation
        w_resume, w_skill, w_roadmap, w_interview = 0.25, 0.35, 0.20, 0.20
        overall = round(
            (w_resume * s_resume) +
            (w_skill * s_skill) +
            (w_roadmap * s_roadmap) +
            (w_interview * s_interview),
            1
        )

        factor_breakdown = {
            "resume": {
                "score": s_resume,
                "weight": w_resume,
                "contribution": round(w_resume * s_resume, 1),
                "reason": resume_reason
            },
            "skills": {
                "score": s_skill,
                "weight": w_skill,
                "contribution": round(w_skill * s_skill, 1),
                "reason": skill_reason
            },
            "roadmap": {
                "score": s_roadmap,
                "weight": w_roadmap,
                "contribution": round(w_roadmap * s_roadmap, 1),
                "reason": roadmap_reason
            },
            "interview": {
                "score": s_interview,
                "weight": w_interview,
                "contribution": round(w_interview * s_interview, 1),
                "reason": interview_reason
            }
        }

        # Save historical record (FR-46, BR-2)
        score_record = ReadinessScore(
            user_id=user_id,
            target_role_id=target_role_id,
            overall_score=overall,
            resume_score_contrib=s_resume,
            skill_score_contrib=s_skill,
            roadmap_score_contrib=s_roadmap,
            interview_score_contrib=s_interview,
            factor_breakdown=factor_breakdown,
            formula_version=cls.FORMULA_VERSION
        )
        db.add(score_record)
        db.commit()

        return {
            "overall_score": overall,
            "target_role": target_role.title if target_role else "Role-Agnostic Core",
            "is_role_specific": bool(target_role),
            "factor_breakdown": factor_breakdown,
            "formula_version": cls.FORMULA_VERSION,
            "calculated_at": score_record.created_at
        }
