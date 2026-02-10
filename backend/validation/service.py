from __future__ import annotations


def validate_answer(generation_output: dict, policy_context: dict) -> dict:
    """Stub post-generation validation checks."""
    checks = {
        "syllabus_alignment": True,
        "factuality": True,
        "safety": len(policy_context.get("safety_flags", [])) == 0,
    }
    return {
        "validated_answer": generation_output["draft_answer"],
        "checks": checks,
    }
