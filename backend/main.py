from __future__ import annotations

from fastapi import FastAPI

from backend.api.handlers import router as api_router

app = FastAPI(title="Student QA Backend")
app.include_router(api_router)
