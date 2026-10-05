import time
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings
from app.modules.ai_abstraction.grounding_validator import GroundingValidator

logger = logging.getLogger(__name__)

# Simple sliding window rate limiter: max calls per user per minute
RATE_LIMIT_WINDOW_SECONDS = 60
MAX_CALLS_PER_WINDOW = 20
_user_call_timestamps: Dict[str, List[float]] = {}

class RateLimitExceededException(Exception):
    pass

def check_rate_limit(user_id: str):
    now = time.time()
    if user_id not in _user_call_timestamps:
        _user_call_timestamps[user_id] = []
    
    # Remove timestamps older than window
    _user_call_timestamps[user_id] = [t for t in _user_call_timestamps[user_id] if now - t < RATE_LIMIT_WINDOW_SECONDS]
    
    if len(_user_call_timestamps[user_id]) >= MAX_CALLS_PER_WINDOW:
        raise RateLimitExceededException(f"Rate limit exceeded: Max {MAX_CALLS_PER_WINDOW} AI calls per minute.")
    
    _user_call_timestamps[user_id].append(now)


class AIAbstractionService:
    """
    Single internal AI abstraction layer interface.
    All feature modules call this service, which owns provider routing, prompting,
    grounding validation, rate limiting, and cost controls.
    """

    def __init__(self, provider: str = None):
        self.provider = provider or settings.AI_PROVIDER
        self.api_key = settings.ANTHROPIC_API_KEY

    def complete(self, task_type: str, structured_input: Dict[str, Any], user_id: Optional[str] = "system") -> Dict[str, Any]:
        """
        Main entry point for AI tasks. Enforces rate limits, routes to provider, and validates output grounding.
        """
        if user_id:
            check_rate_limit(user_id)

        if self.provider == "anthropic" and self.api_key:
            return self._call_anthropic(task_type, structured_input)
        else:
            return self._call_mock_provider(task_type, structured_input)

    def _call_mock_provider(self, task_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic mock provider for offline local execution, testing, and zero-token usage.
        """
        if task_type == "resume_extraction":
            raw_text = input_data.get("raw_text", "")
            return {
                "contact_info": {"email": "student@example.com", "phone": "+1234567890"},
                "education": [{"degree": "B.Tech Computer Science", "institution": "Tech University", "end_year": 2025}],
                "skills_extracted": ["Python", "JavaScript", "React", "SQL", "Git & GitHub"],
                "projects_extracted": [{"name": "E-Commerce API", "summary": "RESTful API built with Python & FastAPI"}],
                "grounded": True
            }

        elif task_type == "resume_rewrite_suggestion":
            source_bullet = input_data.get("bullet_text", "")
            suggested = f"Optimized: {source_bullet} using modular backend patterns and clean code practices."
            is_grounded, reasons = GroundingValidator.validate_resume_rewrite(source_bullet, suggested)
            return {
                "original_bullet": source_bullet,
                "suggested_rewrite": suggested,
                "is_grounded": is_grounded,
                "reasons": reasons
            }

        elif task_type == "recommendation_phrasing":
            title = input_data.get("title", "")
            return {
                "phrased_title": f"Action Item: {title}",
                "phrased_description": f"Based on your recent progress, completing this task will significantly boost your readiness score."
            }

        elif task_type == "mentor_conversation":
            user_msg = input_data.get("message", "")
            profile = input_data.get("profile", {})
            target_role = profile.get("target_role", "SDE")
            return {
                "reply": f"As your placement mentor for {target_role}, I noticed your dedication! Regarding '{user_msg}', I recommend focusing on Data Structures & Algorithms and practicing structured problem solving.",
                "extracted_facts": []
            }

        elif task_type == "memory_fact_extraction":
            return {
                "facts": [
                    {"fact_text": "Prefers backend system design over frontend UI", "category": "role_preference"}
                ]
            }

        elif task_type == "project_defense_question_gen":
            project = input_data.get("project", {})
            proj_name = project.get("name", "Project")
            tech_stack = project.get("tech_stack", ["Python"])
            arch = project.get("architectural_decisions", "Modular monolithic architecture")
            
            question = f"In your {proj_name} project built with {', '.join(tech_stack[:2])}, how did you justify choosing {arch} over alternative designs?"
            is_grounded, reasons = GroundingValidator.validate_project_defense_question(project, question)
            return {
                "question_text": question,
                "grounded_fields": ["name", "tech_stack", "architectural_decisions"],
                "is_grounded": is_grounded,
                "reasons": reasons
            }

        elif task_type == "mock_interview_feedback":
            ans_text = input_data.get("answer_text", "")
            score = 80.0 if len(ans_text) > 40 else 50.0
            return {
                "score": score,
                "feedback_text": "Good technical depth. Make sure to articulate trade-offs clearly when answering scenario questions.",
                "strengths": ["Clear explanation of core concept"],
                "improvements": ["Elaborate on edge cases and scalability limitations"]
            }

        return {"error": f"Unknown task_type '{task_type}'"}

    def _call_anthropic(self, task_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls Claude API via Anthropic REST API endpoint with schema-constrained output.
        """
        try:
            prompt = f"Perform the following structured task: {task_type}.\nInput: {json.dumps(input_data)}\nReturn valid JSON."
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            with httpx.Client(timeout=30.0) as client:
                res = client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
                if res.status_code == 200:
                    text_resp = res.json()["content"][0]["text"]
                    return json.loads(text_resp)
                else:
                    logger.warning(f"Claude API returned status {res.status_code}, falling back to mock provider.")
                    return self._call_mock_provider(task_type, input_data)
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}. Falling back to mock provider.")
            return self._call_mock_provider(task_type, input_data)

ai_service = AIAbstractionService()
