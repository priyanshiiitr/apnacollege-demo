"""LLM client wrapper that enforces context-only answer generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from backend.generation.prompt_builder import PromptOptions, build_prompt


@dataclass(frozen=True)
class GenerationOutput:
    """Container for model output and confidence information."""

    answer: str
    prompt: str
    retrieval_coverage: float
    syllabus_alignment_percentage: float


class ContextOnlyLLMClient:
    """Thin client that only generates from retrieved context."""

    def __init__(self, model_callable: Callable[[str], str]):
        """Args:
        model_callable: Callable that accepts a prompt and returns generated text.
        """
        self._model_callable = model_callable

    @staticmethod
    def _estimate_retrieval_coverage(question: str, context_chunks: Sequence[str]) -> float:
        q_terms = {t.lower() for t in question.split() if len(t.strip(".,!?;:")) >= 4 for t in [t.strip(".,!?;:")]}
        if not q_terms:
            return 1.0 if context_chunks else 0.0

        context_text = " ".join(context_chunks).lower()
        matched = sum(1 for term in q_terms if term in context_text)
        return min(1.0, matched / len(q_terms))

    def generate(
        self,
        question: str,
        context_chunks: Iterable[str],
        options: PromptOptions | None = None,
    ) -> GenerationOutput:
        chunks = [c for c in context_chunks if c and c.strip()]
        prompt = build_prompt(question=question, context_chunks=chunks, options=options)
        answer = self._model_callable(prompt).strip()

        retrieval_coverage = self._estimate_retrieval_coverage(question, chunks)
        syllabus_alignment_percentage = round(retrieval_coverage * 100, 2)

        return GenerationOutput(
            answer=answer,
            prompt=prompt,
            retrieval_coverage=retrieval_coverage,
            syllabus_alignment_percentage=syllabus_alignment_percentage,
        )
