from __future__ import annotations

from backend.models import AnswerResponse


def format_student_response(validated_output: dict, policy_context: dict) -> AnswerResponse:
    """Stub response shaping for student-friendly output."""
    checks = validated_output["checks"]
    rationale = (
        "Generated using retrieval, policy filters, and validation checks: "
        f"{', '.join([key for key, passed in checks.items() if passed])}."
    )
    return AnswerResponse(
        answer=validated_output["validated_answer"],
        rationale=rationale,
        sources=policy_context["retrieved_context"]["dense_hits"],
        safety_notes=policy_context.get("safety_flags", []),
    )
