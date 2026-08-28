from datetime import datetime

from pydantic import BaseModel


class EvaluationRetrievedSource(BaseModel):
    rank: int

    chunk_id: int

    incident_code: str | None = None

    document_title: str

    section: str

    similarity: float


class EvaluationQuestionResult(BaseModel):
    question_id: str

    question: str

    passed: bool

    expected_sources: list[str]

    retrieved_sources: list[
        EvaluationRetrievedSource
    ]

    duration_ms: float


class EvaluationSummary(BaseModel):
    metric: str

    top_k: int

    total_questions: int

    passed_questions: int

    failed_questions: int

    score_percent: float

    average_retrieval_ms: float

    generated_at: datetime

    results: list[
        EvaluationQuestionResult
    ]