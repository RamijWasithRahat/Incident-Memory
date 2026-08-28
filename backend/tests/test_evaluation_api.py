from datetime import (
    datetime,
    timezone,
)

from fastapi.testclient import (
    TestClient,
)

from app.main import app

from app.schemas.evaluation import (
    EvaluationSummary,
)


client = TestClient(app)


def make_summary(
) -> EvaluationSummary:
    return EvaluationSummary(
        metric=(
            "top_3_retrieval_success"
        ),

        top_k=3,

        total_questions=30,

        passed_questions=27,

        failed_questions=3,

        score_percent=90.0,

        average_retrieval_ms=25.0,

        generated_at=datetime.now(
            timezone.utc
        ),

        results=[],
    )


def test_run_evaluation_endpoint(
    monkeypatch,
) -> None:
    summary = make_summary()

    def fake_run(
        db,
        *,
        top_k,
    ):
        assert top_k == 3

        return summary

    monkeypatch.setattr(
        "app.api.evaluation."
        "run_retrieval_evaluation",
        fake_run,
    )

    response = client.post(
        "/api/evaluation/run"
    )

    assert (
        response.status_code
        == 200
    )

    body = response.json()

    assert (
        body["metric"]
        == "top_3_retrieval_success"
    )

    assert (
        body["total_questions"]
        == 30
    )

    assert (
        body["score_percent"]
        == 90.0
    )


def test_get_evaluation_results_endpoint(
    monkeypatch,
) -> None:
    summary = make_summary()

    monkeypatch.setattr(
        "app.api.evaluation."
        "load_latest_evaluation",
        lambda: summary,
    )

    response = client.get(
        "/api/evaluation/results"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()[
            "passed_questions"
        ]
        == 27
    )