from __future__ import annotations

from backend.formatting.service import format_student_response
from backend.generation.service import generate_draft_answer
from backend.models import AnswerRequest, AnswerResponse
from backend.policy.service import apply_policy_constraints
from backend.retrieval.service import retrieve_context
from backend.validation.service import validate_answer


def answer_student_query(request: AnswerRequest) -> AnswerResponse:
    """Run all backend layers in sequence for answering a student query."""
    retrieved_context = retrieve_context(request)
    policy_context = apply_policy_constraints(request, retrieved_context)
    generation_output = generate_draft_answer(request, policy_context)
    validated_output = validate_answer(generation_output, policy_context)
    return format_student_response(validated_output, policy_context)
