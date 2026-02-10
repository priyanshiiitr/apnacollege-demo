from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AnswerRequest(BaseModel):
    class_level: int = Field(alias="class", ge=6, le=10)
    board: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    chapter: str = Field(min_length=1)
    proficiency: Literal["beginner", "intermediate", "advanced"]
    question: str = Field(min_length=1)

    model_config = {
        "populate_by_name": True,
    }


class AnswerResponse(BaseModel):
    answer: str
    rationale: str
    sources: list[str]
    safety_notes: list[str] = Field(default_factory=list)
