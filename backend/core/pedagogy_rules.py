"""Pedagogy adapter rules for turning profile data into response constraints."""

from __future__ import annotations

from dataclasses import dataclass

from backend.core.student_profile import StudentProfile


@dataclass(frozen=True)
class PedagogyContext:
    """Derived pedagogical settings based on student profile."""

    max_response_length: int
    language_difficulty: str
    explanation_style: str
    allowed_examples_count: int


def derive_pedagogy_context(profile: StudentProfile) -> PedagogyContext:
    """Derive response controls from a normalized student profile."""

    proficiency = profile.proficiency
    class_level = _parse_class_level(profile.class_level)

    if proficiency == "beginner":
        base_max_length = 180
        language_difficulty = "simple"
        explanation_style = "story-based"
        allowed_examples_count = 3
    elif proficiency == "intermediate":
        base_max_length = 260
        language_difficulty = "moderate"
        explanation_style = "story-based" if class_level <= 8 else "formula-based"
        allowed_examples_count = 2
    else:
        base_max_length = 340
        language_difficulty = "advanced"
        explanation_style = "formula-based"
        allowed_examples_count = 1

    if class_level <= 5:
        base_max_length -= 20

    return PedagogyContext(
        max_response_length=max(base_max_length, 120),
        language_difficulty=language_difficulty,
        explanation_style=explanation_style,
        allowed_examples_count=allowed_examples_count,
    )


def _parse_class_level(class_level: str) -> int:
    digits = "".join(ch for ch in class_level if ch.isdigit())
    return int(digits) if digits else 0
