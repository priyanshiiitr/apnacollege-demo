from __future__ import annotations

from backend.models import AnswerRequest


def generate_draft_answer(request: AnswerRequest, policy_context: dict) -> dict:
    """Stub LLM generation + guardrails layer."""
    supporting_points = policy_context["retrieved_context"]["dense_hits"]
    draft = (
        f"Let's solve this step-by-step for {request.subject}. "
        f"From chapter '{request.chapter}', remember: {supporting_points[0]}."
    )

    return {
        "draft_answer": draft,
        "guardrails_applied": ["age-appropriate tone", "curriculum-bounded response"],
    }
