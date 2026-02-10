"""Shared normalized context object for all downstream layers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from backend.core.pedagogy_rules import PedagogyContext, derive_pedagogy_context
from backend.core.student_profile import StudentProfile


@dataclass(frozen=True)
class NormalizedLearningContext:
    """Payload every downstream layer must consume."""

    student_profile: StudentProfile
    pedagogy: PedagogyContext


def build_normalized_context(payload: Mapping[str, Any]) -> NormalizedLearningContext:
    """Validate request payload and build normalized context."""
    profile = StudentProfile.from_payload(payload)
    pedagogy = derive_pedagogy_context(profile)
    return NormalizedLearningContext(student_profile=profile, pedagogy=pedagogy)
