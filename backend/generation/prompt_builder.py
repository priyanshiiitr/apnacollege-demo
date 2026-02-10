"""Prompt builder for strict, teacher-style context-grounded generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PromptOptions:
    """Controls strictness for context-only generation prompts."""

    strictness_level: int = 1
    include_exam_tone: bool = True


def _teacher_constraints(strictness_level: int) -> str:
    base = [
        "You are a strict, syllabus-aligned teacher.",
        "Use ONLY the provided CONTEXT chunks.",
        "Do NOT add external facts, assumptions, examples, dates, names, or definitions that are absent from the context.",
        "If context is incomplete, explicitly say: 'Not enough evidence in provided context.'",
        "Every sentence must be traceable to at least one context chunk.",
    ]
    if strictness_level >= 2:
        base.extend(
            [
                "Do not use background world knowledge.",
                "Do not infer beyond direct statements unless the inference is explicitly supported by multiple chunks.",
            ]
        )
    if strictness_level >= 3:
        base.extend(
            [
                "When uncertain, omit the claim.",
                "Prefer shorter output over potentially unsupported detail.",
            ]
        )
    return "\n".join(f"- {line}" for line in base)


def build_prompt(question: str, context_chunks: Iterable[str], options: PromptOptions | None = None) -> str:
    """Builds a strict prompt that forbids external facts.

    Args:
        question: Student question to answer.
        context_chunks: Retrieved syllabus/reference chunks.
        options: Prompt behavior controls.

    Returns:
        A complete prompt string for a model call.
    """
    opts = options or PromptOptions()
    chunks = [chunk.strip() for chunk in context_chunks if chunk and chunk.strip()]
    formatted_chunks = "\n\n".join(f"[CHUNK {i+1}]\n{chunk}" for i, chunk in enumerate(chunks))

    tone = "Answer in clear teacher style with exam-oriented clarity." if opts.include_exam_tone else ""

    return (
        "SYSTEM INSTRUCTIONS\n"
        f"{_teacher_constraints(opts.strictness_level)}\n\n"
        "OUTPUT RULES\n"
        "- Structure with concise paragraphs or bullets.\n"
        "- No fabricated content.\n"
        "- Keep language simple and student friendly.\n"
        f"- {tone}\n\n"
        "CONTEXT (authoritative)\n"
        f"{formatted_chunks if formatted_chunks else '[NO CONTEXT PROVIDED]'}\n\n"
        "TASK\n"
        f"Question: {question.strip()}\n"
        "Write an answer strictly grounded in the context."
    )
