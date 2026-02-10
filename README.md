# apnacollege-demo

This repository now includes a modular backend scaffold for answering student questions.

## Backend structure

- `backend/api/` – HTTP request handlers.
- `backend/core/` – orchestration entrypoint.
- `backend/retrieval/` – dense/sparse/KG/QA retrieval layer.
- `backend/policy/` – syllabus and safety constraints.
- `backend/generation/` – draft answer generation with guardrails.
- `backend/validation/` – post-generation checks.
- `backend/formatting/` – student-friendly response shaping.

## Endpoint

`POST /answer`

Expected payload fields:

- `class` (6–10)
- `board`
- `subject`
- `chapter`
- `proficiency` (`beginner`, `intermediate`, `advanced`)
- `question`

Run the API (when dependencies are installed):

```bash
uvicorn backend.main:app --reload
```
