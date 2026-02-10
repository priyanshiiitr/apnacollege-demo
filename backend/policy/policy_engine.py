"""Policy engine for intent, syllabus alignment, and response shaping.

This module is designed to run *before* any LLM call.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Callable

SAFE_OUT_OF_SYLLABUS_RESPONSE = (
    "This topic is not required for your class syllabus. Let’s focus on what you need for exams."
)

INTENT_LABELS = (
    "definition",
    "numerical",
    "conceptual",
    "why/how",
    "exam",
    "doubt",
)

# Canonical structure: class -> board -> subject -> set(chapters)
DEFAULT_SYLLABUS_MAP: dict[str, dict[str, dict[str, set[str]]]] = {
    "10": {
        "cbse": {
            "science": {
                "chemical reactions and equations",
                "acids bases and salts",
                "metals and non-metals",
                "carbon and its compounds",
                "life processes",
                "light reflection and refraction",
            },
            "mathematics": {
                "real numbers",
                "polynomials",
                "quadratic equations",
                "arithmetic progressions",
                "triangles",
                "circles",
            },
        }
    },
    "12": {
        "cbse": {
            "physics": {
                "electric charges and fields",
                "electrostatic potential and capacitance",
                "current electricity",
                "moving charges and magnetism",
            },
            "chemistry": {
                "solid state",
                "solutions",
                "electrochemistry",
                "chemical kinetics",
            },
        }
    },
}


@dataclass(slots=True)
class PolicyDecision:
    """Decision output from policy engine before LLM execution."""

    proceed_to_llm: bool
    intent: str
    filtered_chunks: list[dict[str, Any]] = field(default_factory=list)
    llm_constraints: dict[str, Any] = field(default_factory=dict)
    safe_response: str | None = None
    reason: str | None = None


def _normalize(text: str | None) -> str:
    if not text:
        return ""
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return normalized


def classify_intent(query: str) -> str:
    """Classify a student query into one of the supported intent labels."""

    q = _normalize(query)
    if any(token in q for token in ("define", "definition", "meaning of", "what is")):
        return "definition"
    if any(token in q for token in ("numerical", "calculate", "solve", "find value", "compute")):
        return "numerical"
    if any(token in q for token in ("why", "how", "explain why", "explain how")):
        return "why/how"
    if any(token in q for token in ("exam", "important", "board question", "marks", "pyq")):
        return "exam"
    if any(token in q for token in ("doubt", "confused", "not clear", "didn't understand")):
        return "doubt"
    return "conceptual"


def _extract_syllabus_keys(academic_context: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        _normalize(str(academic_context.get("class", ""))),
        _normalize(str(academic_context.get("board", ""))),
        _normalize(str(academic_context.get("subject", ""))),
        _normalize(str(academic_context.get("chapter", ""))),
    )


def is_in_syllabus(
    academic_context: dict[str, Any],
    syllabus_map: dict[str, dict[str, dict[str, set[str]]]] | None = None,
) -> bool:
    """Verify class + board + subject + chapter mapping against syllabus graph."""

    if syllabus_map is None:
        syllabus_map = DEFAULT_SYLLABUS_MAP

    class_name, board, subject, chapter = _extract_syllabus_keys(academic_context)

    # Must have all dimensions to pass strict syllabus check.
    if not all((class_name, board, subject, chapter)):
        return False

    return chapter in syllabus_map.get(class_name, {}).get(board, {}).get(subject, set())


def hard_filter_chunks(
    chunks: list[dict[str, Any]],
    allowed_graph_nodes: set[str],
) -> list[dict[str, Any]]:
    """Drop chunks whose syllabus graph node is not allowed."""

    filtered: list[dict[str, Any]] = []
    for chunk in chunks:
        node = _normalize(str(chunk.get("syllabus_node") or chunk.get("chapter") or ""))
        if node and node in allowed_graph_nodes:
            filtered.append(chunk)
    return filtered


def _simplify_text(text: str) -> str:
    text = re.sub(r"\((.*?)\)", "", text)  # remove parenthetical complexity
    text = re.sub(r"\s+", " ", text).strip()

    sentences = re.split(r"(?<=[.!?])\s+", text)
    simplified: list[str] = []
    for sentence in sentences:
        words = sentence.split()
        if len(words) > 18:
            sentence = " ".join(words[:18]).rstrip(" ,") + "..."
        simplified.append(sentence)
    return " ".join(simplified).strip()


def _cap_examples(text: str, max_examples: int) -> str:
    pattern = re.compile(r"(?i)\bfor example\b|\bexample\s*\d*\s*:")
    matches = list(pattern.finditer(text))
    if len(matches) <= max_examples:
        return text

    cutoff = matches[max_examples].start()
    return text[:cutoff].rstrip()


def soft_filter_response(text: str, intent: str) -> str:
    """Apply soft response constraints: simpler language, lighter analogies, fewer examples."""

    constrained = _simplify_text(text)

    # Limit analogy complexity by removing nested analogy markers.
    constrained = re.sub(r"(?i)\blike\s+(.+?)\s+like\b", "like", constrained)

    # Cap examples (numerical/exam can have more).
    max_examples = 2 if intent in {"numerical", "exam"} else 1
    constrained = _cap_examples(constrained, max_examples=max_examples)
    return constrained


class PolicyEngine:
    """Syllabus and response policy enforcement layer."""

    def __init__(
        self,
        syllabus_map: dict[str, dict[str, dict[str, set[str]]]] | None = None,
    ) -> None:
        self.syllabus_map = syllabus_map or DEFAULT_SYLLABUS_MAP

    def evaluate(
        self,
        query: str,
        academic_context: dict[str, Any],
        chunks: list[dict[str, Any]],
    ) -> PolicyDecision:
        intent = classify_intent(query)

        if not is_in_syllabus(academic_context, self.syllabus_map):
            return PolicyDecision(
                proceed_to_llm=False,
                intent=intent,
                safe_response=SAFE_OUT_OF_SYLLABUS_RESPONSE,
                reason="out_of_syllabus",
            )

        class_name, board, subject, _ = _extract_syllabus_keys(academic_context)
        allowed_nodes = self.syllabus_map[class_name][board][subject]
        kept_chunks = hard_filter_chunks(chunks, allowed_nodes)

        constraints = {
            "simplify_language": True,
            "analogy_complexity": "low",
            "max_examples": 2 if intent in {"numerical", "exam"} else 1,
        }

        return PolicyDecision(
            proceed_to_llm=True,
            intent=intent,
            filtered_chunks=kept_chunks,
            llm_constraints=constraints,
        )


def apply_policy_before_llm(
    query: str,
    academic_context: dict[str, Any],
    chunks: list[dict[str, Any]],
    llm_callable: Callable[..., str],
    *,
    policy_engine: PolicyEngine | None = None,
) -> str:
    """Run policy checks before any LLM call and return a safe or constrained response."""

    engine = policy_engine or PolicyEngine()
    decision = engine.evaluate(query=query, academic_context=academic_context, chunks=chunks)

    if not decision.proceed_to_llm:
        return decision.safe_response or SAFE_OUT_OF_SYLLABUS_RESPONSE

    raw_response = llm_callable(
        query=query,
        chunks=decision.filtered_chunks,
        intent=decision.intent,
        constraints=decision.llm_constraints,
    )
    return soft_filter_response(raw_response, decision.intent)
