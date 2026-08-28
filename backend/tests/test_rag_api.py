from fastapi.testclient import TestClient

from app.main import app
from app.schemas.rag import (
    RAGAskResponse,
)


client = TestClient(app)


def test_rag_endpoint(
    monkeypatch,
) -> None:
    fake_response = RAGAskResponse(
        question="What caused INC-012?",
        answer=(
            "The historical incident was caused "
            "by connection pool exhaustion [S1]."
        ),
        insufficient_evidence=False,
        model=(
            "Qwen/Qwen2.5-0.5B-Instruct"
        ),
        evidence_count=1,
        sources=[],
    )

    def fake_answer_rag_question(
        db,
        question,
        **kwargs,
    ):
        return fake_response

    monkeypatch.setattr(
        "app.api.rag.answer_rag_question",
        fake_answer_rag_question,
    )

    response = client.post(
        "/api/rag/ask",
        json={
            "question": (
                "What caused INC-012?"
            ),
            "top_k": 5,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["insufficient_evidence"]
        is False
    )

    assert "[S1]" in body["answer"]


def test_blank_question_rejected() -> None:
    response = client.post(
        "/api/rag/ask",
        json={
            "question": " ",
        },
    )

    assert response.status_code == 422


def test_invalid_top_k_rejected() -> None:
    response = client.post(
        "/api/rag/ask",
        json={
            "question": (
                "What caused INC-012?"
            ),
            "top_k": 100,
        },
    )

    assert response.status_code == 422