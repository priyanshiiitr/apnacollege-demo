"""Retry/fallback orchestration for stricter grounded regeneration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from backend.generation.llm_client import ContextOnlyLLMClient
from backend.generation.prompt_builder import PromptOptions
from backend.validation.answer_validator import AnswerValidator, ValidationResult


@dataclass(frozen=True)
class RegenerationResult:
    answer: str
    validation: ValidationResult
    attempts_used: int
    used_fallback: bool
    retrieval_coverage: float
    syllabus_alignment_percentage: float


class RegenerationEngine:
    """Retries generation with increasing strictness, then safe fallback."""

    def __init__(self, client: ContextOnlyLLMClient, validator: AnswerValidator):
        self.client = client
        self.validator = validator

    @staticmethod
    def _safe_fallback(question: str, context_chunks: list[str]) -> str:
        if not context_chunks:
            return (
                "### Safe Answer\n"
                "Not enough evidence in provided context.\n\n"
                "Please provide relevant syllabus chunks to answer this question accurately."
            )

        top = "\n".join(f"- {chunk[:180].strip()}" for chunk in context_chunks[:3])
        return (
            "### Safe Answer (Context-Limited)\n"
            "Not enough evidence in provided context for a fully validated response.\n"
            "Here are directly retrieved points:\n"
            f"{top}"
        )

    def generate_with_retry(
        self,
        question: str,
        context_chunks: Iterable[str],
        max_attempts: int = 3,
    ) -> RegenerationResult:
        chunks = [c for c in context_chunks if c and c.strip()]

        last_validation: ValidationResult | None = None
        last_answer = ""
        last_coverage = 0.0

        for attempt in range(1, max_attempts + 1):
            options = PromptOptions(strictness_level=min(3, attempt), include_exam_tone=True)
            generation = self.client.generate(question=question, context_chunks=chunks, options=options)
            validation = self.validator.validate(generation.answer, chunks)

            last_validation = validation
            last_answer = generation.answer
            last_coverage = generation.retrieval_coverage

            if validation.is_valid:
                confidence = round(((generation.retrieval_coverage + validation.validation_pass_rate) / 2) * 100, 2)
                return RegenerationResult(
                    answer=generation.answer,
                    validation=validation,
                    attempts_used=attempt,
                    used_fallback=False,
                    retrieval_coverage=generation.retrieval_coverage,
                    syllabus_alignment_percentage=confidence,
                )

        assert last_validation is not None
        fallback = self._safe_fallback(question, chunks)
        fallback_validation = self.validator.validate(fallback, chunks)
        confidence = round(((last_coverage + last_validation.validation_pass_rate) / 2) * 100, 2)
        return RegenerationResult(
            answer=fallback,
            validation=fallback_validation,
            attempts_used=max_attempts,
            used_fallback=True,
            retrieval_coverage=last_coverage,
            syllabus_alignment_percentage=confidence,
        )
