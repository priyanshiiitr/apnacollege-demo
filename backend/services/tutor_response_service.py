"""Example downstream service that relies on normalized context only."""

from __future__ import annotations

from backend.core.context import NormalizedLearningContext


class InvalidContextError(ValueError):
    """Raised when downstream layer is called without normalized context."""


def build_response_prompt(
    question: str,
    context: NormalizedLearningContext,
) -> str:
    """Create a constrained prompt for a tutoring model."""

    if not isinstance(context, NormalizedLearningContext):
        raise InvalidContextError(
            "Downstream services must receive a NormalizedLearningContext instance."
        )

    pedagogy = context.pedagogy
    profile = context.student_profile

    return (
        f"Answer as a {profile.board} {profile.class_level} {profile.subject} tutor for "
        f"chapter '{profile.chapter}'. Keep answer <= {pedagogy.max_response_length} words, "
        f"use {pedagogy.language_difficulty} language, prefer {pedagogy.explanation_style} "
        f"explanations, and include at most {pedagogy.allowed_examples_count} examples. "
        f"Question: {question.strip()}"
    )
