"""Student-friendly formatter for validated answers."""

from __future__ import annotations

import re
from typing import Iterable

FORMULA_PATTERN = re.compile(r"([A-Za-z][A-Za-z0-9_]*\s*=\s*[^\n,.]+)")


def _to_bullets(lines: Iterable[str]) -> str:
    cleaned = [line.strip(" -") for line in lines if line and line.strip()]
    return "\n".join(f"- {line}" for line in cleaned)


def format_student_answer(question: str, raw_answer: str, exam_tips: list[str] | None = None) -> str:
    """Formats answer with headings, bullets, formulas, and memory cues."""
    tips = exam_tips or [
        "Write definitions exactly as given in the syllabus language.",
        "Use stepwise points and underline keywords.",
        "Revise formulas before attempting numericals.",
    ]

    paragraphs = [p.strip() for p in re.split(r"\n+", raw_answer) if p.strip()]
    bullet_block = _to_bullets(paragraphs)

    formulas = FORMULA_PATTERN.findall(raw_answer)
    formula_block = _to_bullets([f"**{f.strip()}**" for f in formulas]) if formulas else "- No explicit formula found in context-based answer."

    remember = paragraphs[0] if paragraphs else "Not enough evidence in provided context."

    return (
        f"## Question\n{question.strip()}\n\n"
        "## Explained Answer\n"
        f"{bullet_block}\n\n"
        "## Formula Highlights\n"
        f"{formula_block}\n\n"
        "## Exam Tips\n"
        f"{_to_bullets(tips)}\n\n"
        "## Remember this\n"
        f"- {remember}"
    )
