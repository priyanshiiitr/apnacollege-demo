from __future__ import annotations

from backend.models import AnswerRequest


def retrieve_context(request: AnswerRequest) -> dict:
    """Stub retrieval pipeline for dense/sparse/KG/QA lookups."""
    return {
        "dense_hits": [f"Dense note for {request.subject} - {request.chapter}"],
        "sparse_hits": [f"Keyword hit for question: {request.question[:40]}"],
        "kg_facts": [f"Curriculum graph node for class {request.class_level}"],
        "qa_pairs": ["Previously asked similar classroom question."],
    }
