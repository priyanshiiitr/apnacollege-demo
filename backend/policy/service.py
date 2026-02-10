from __future__ import annotations

from backend.models import AnswerRequest


def apply_policy_constraints(request: AnswerRequest, retrieved_context: dict) -> dict:
    """Stub policy checks for syllabus alignment and safety constraints."""
    safety_flags: list[str] = []
    if "harm" in request.question.lower():
        safety_flags.append("Potentially unsafe phrasing detected.")

    return {
        "syllabus_scope": f"{request.board} class {request.class_level} {request.subject}",
        "allowed_depth": request.proficiency,
        "safety_flags": safety_flags,
        "retrieved_context": retrieved_context,
    }
