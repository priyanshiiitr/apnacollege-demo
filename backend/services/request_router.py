"""Request entrypoint that enforces profile requirements."""

from __future__ import annotations

from typing import Any, Mapping

from backend.core.context import build_normalized_context
from backend.services.tutor_response_service import build_response_prompt


def handle_tutor_request(payload: Mapping[str, Any]) -> str:
    """Validate payload, normalize context, and dispatch to downstream layer."""

    context = build_normalized_context(payload)
    question = str(payload.get("question", "")).strip()
    return build_response_prompt(question=question, context=context)
