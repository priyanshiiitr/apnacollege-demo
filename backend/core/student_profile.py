"""Student profile domain model and normalization helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

REQUIRED_PROFILE_FIELDS = (
    "class_level",
    "board",
    "subject",
    "chapter",
    "proficiency",
)


class StudentProfileValidationError(ValueError):
    """Raised when incoming profile payload is missing required fields."""


@dataclass(frozen=True)
class StudentProfile:
    """Normalized student profile used across downstream layers."""

    class_level: str
    board: str
    subject: str
    chapter: str
    proficiency: str

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "StudentProfile":
        """Build and validate a student profile from request payload data."""
        missing = [field for field in REQUIRED_PROFILE_FIELDS if not payload.get(field)]
        if missing:
            missing_str = ", ".join(missing)
            raise StudentProfileValidationError(
                f"Missing required profile fields: {missing_str}"
            )

        return cls(
            class_level=str(payload["class_level"]).strip(),
            board=str(payload["board"]).strip(),
            subject=str(payload["subject"]).strip(),
            chapter=str(payload["chapter"]).strip(),
            proficiency=str(payload["proficiency"]).strip().lower(),
        )
