import re
from typing import Dict, Any, List, Tuple

class GroundingValidator:
    """
    Validates that AI-generated content (resume extractions, bullet rewrites, project defense questions)
    is strictly grounded in the source text provided by the user. Prevents hallucinating or inventing facts.
    """

    @staticmethod
    def validate_resume_rewrite(source_text: str, suggested_text: str) -> Tuple[bool, List[str]]:
        """
        Validates a resume bullet rewrite suggestion against original resume source text.
        Rule: Must rephrase or format existing details; must not invent new metrics, company names, or tools.
        """
        unsupported = []
        
        # Check for numbers/metrics that were not in the original source text
        orig_numbers = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', source_text))
        sugg_numbers = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', suggested_text))

        new_numbers = sugg_numbers - orig_numbers
        if new_numbers:
            unsupported.append(f"Introduced unsupported metrics/numbers: {', '.join(new_numbers)}")

        # Check for capitalized proper nouns/technologies not in source
        orig_words = set(w.lower() for w in re.findall(r'\b[A-Za-z0-9+#\.]+\b', source_text))
        sugg_words = set(re.findall(r'\b[A-Z][A-Za-z0-9+#\.]+\b', suggested_text))

        for word in sugg_words:
            if word.lower() not in orig_words and len(word) > 2:
                # Exclude common sentence starters
                if word.upper() not in ["THE", "AND", "FOR", "WITH", "BUILT", "CREATED", "DEVELOPED", "DESIGNED", "IMPROVED", "IMPLEMENTED", "UTILIZED"]:
                    unsupported.append(f"Introduced ungrounded entity/term: '{word}'")

        is_grounded = len(unsupported) == 0
        return is_grounded, unsupported

    @staticmethod
    def validate_project_defense_question(project_fields: Dict[str, Any], question_text: str) -> Tuple[bool, List[str]]:
        """
        Validates that a generated project defense question is grounded in the student's structured project fields.
        """
        unsupported = []
        combined_source = " ".join([
            str(project_fields.get("name", "")),
            str(project_fields.get("role", "")),
            " ".join(project_fields.get("tech_stack", [])),
            str(project_fields.get("architectural_decisions", "")),
            str(project_fields.get("challenges_faced", "")),
            str(project_fields.get("tradeoffs_made", ""))
        ]).lower()

        STOP_WORDS = {
            "the", "and", "for", "with", "why", "how", "was", "what", "where", "when",
            "which", "from", "over", "under", "did", "you", "choose", "your", "this",
            "that", "have", "been", "were", "are", "about", "into"
        }
        
        # Check if question references at least one domain keyword from the project (excluding stop words)
        key_terms = set(w for w in re.findall(r'\b[a-zA-Z]{3,}\b', combined_source) if w not in STOP_WORDS)
        question_words = set(w for w in re.findall(r'\b[a-zA-Z]{3,}\b', question_text.lower()) if w not in STOP_WORDS)

        overlap = question_words.intersection(key_terms)
        if not overlap:
            unsupported.append("Question does not reference any specific concept or technology from the project entry.")

        is_grounded = len(unsupported) == 0
        return is_grounded, unsupported
