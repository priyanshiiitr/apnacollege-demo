"""Validation to ensure generated answers are grounded in retrieved chunks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
    "this",
    "these",
    "those",
}


@dataclass(frozen=True)
class SentenceValidation:
    sentence: str
    supported: bool
    supporting_chunk_ids: list[int]


@dataclass(frozen=True)
class ValidationResult:
    per_sentence: list[SentenceValidation]
    unsupported_terms: list[str]
    validation_pass_rate: float
    is_valid: bool


class AnswerValidator:
    """Checks sentence-to-chunk mapping and unsupported term detection."""

    def __init__(self, overlap_threshold: float = 0.35, min_tokens: int = 2):
        self.overlap_threshold = overlap_threshold
        self.min_tokens = min_tokens

    @staticmethod
    def _normalize_tokens(text: str) -> set[str]:
        tokens = re.findall(r"[A-Za-z0-9_+-]+", text.lower())
        return {t for t in tokens if len(t) >= 3 and t not in STOPWORDS}

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        return [p.strip() for p in parts if p.strip()]

    def _supporting_chunk_ids(self, sentence: str, chunk_tokens: Sequence[set[str]]) -> list[int]:
        sentence_tokens = self._normalize_tokens(sentence)
        if len(sentence_tokens) < self.min_tokens:
            return []

        supported_by: list[int] = []
        for idx, c_tokens in enumerate(chunk_tokens):
            if not c_tokens:
                continue
            overlap = len(sentence_tokens & c_tokens)
            ratio = overlap / max(1, len(sentence_tokens))
            if ratio >= self.overlap_threshold:
                supported_by.append(idx + 1)
        return supported_by

    def validate(self, answer: str, context_chunks: Iterable[str]) -> ValidationResult:
        chunks = [c for c in context_chunks if c and c.strip()]
        chunk_tokens = [self._normalize_tokens(c) for c in chunks]
        context_vocab = set().union(*chunk_tokens) if chunk_tokens else set()

        sentences = self._split_sentences(answer)
        per_sentence: list[SentenceValidation] = []
        unsupported_terms_all: set[str] = set()

        for sentence in sentences:
            supporting_ids = self._supporting_chunk_ids(sentence, chunk_tokens)
            supported = len(supporting_ids) > 0
            per_sentence.append(
                SentenceValidation(
                    sentence=sentence,
                    supported=supported,
                    supporting_chunk_ids=supporting_ids,
                )
            )

            sentence_terms = self._normalize_tokens(sentence)
            new_terms = {t for t in sentence_terms if t not in context_vocab}
            unsupported_terms_all.update(new_terms)

        if not per_sentence:
            return ValidationResult([], [], 0.0, False)

        supported_count = sum(1 for s in per_sentence if s.supported)
        pass_rate = supported_count / len(per_sentence)
        is_valid = pass_rate >= 0.95 and len(unsupported_terms_all) == 0

        return ValidationResult(
            per_sentence=per_sentence,
            unsupported_terms=sorted(unsupported_terms_all),
            validation_pass_rate=pass_rate,
            is_valid=is_valid,
        )
