from __future__ import annotations

from fastapi import APIRouter

from backend.core.orchestrator import answer_student_query
from backend.models import AnswerRequest, AnswerResponse

router = APIRouter()


@router.post("/answer", response_model=AnswerResponse)
def post_answer(request: AnswerRequest) -> AnswerResponse:
    return answer_student_query(request)
