import csv
import json

from datetime import (
    datetime,
    timezone,
)
from pathlib import Path
from time import perf_counter

from sqlalchemy.orm import Session

from app.schemas.evaluation import (
    EvaluationQuestionResult,
    EvaluationRetrievedSource,
    EvaluationSummary,
)
from app.services.rag_service import (
    RetrievedEvidence,
    retrieve_rag_evidence,
)


GOLDEN_SET_PATH = Path(
    "/data/evaluation/golden_questions.json"
)

RESULTS_DIR = Path(
    "/data/evaluation/results"
)

LATEST_JSON_PATH = (
    RESULTS_DIR / "latest.json"
)

LATEST_CSV_PATH = (
    RESULTS_DIR / "latest.csv"
)


def _normalize_text(
    value: str | None,
) -> str:
    if value is None:
        return ""

    return (
        value.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def _source_matches(
    expected: dict,
    actual: RetrievedEvidence,
) -> bool:
    expected_incident = (
        expected.get(
            "incident_code"
        )
    )

    if expected_incident:
        if (
            _normalize_text(
                expected_incident
            )
            != _normalize_text(
                actual.incident_code
            )
        ):
            return False

    expected_section = (
        expected.get(
            "section"
        )
    )

    if expected_section:
        if (
            _normalize_text(
                expected_section
            )
            != _normalize_text(
                actual.section
            )
        ):
            return False

    title_contains = (
        expected.get(
            "document_title_contains"
        )
    )

    if title_contains:
        if (
            title_contains.strip().lower()
            not in
            actual.document_title
            .strip()
            .lower()
        ):
            return False

    return True


def _expected_source_label(
    expected: dict,
) -> str:
    incident_code = (
        expected.get(
            "incident_code"
        )
    )

    title = (
        expected.get(
            "document_title_contains"
        )
    )

    section = (
        expected.get(
            "section"
        )
    )

    source = (
        incident_code
        or title
        or "Unknown source"
    )

    if section:
        return (
            f"{source} / {section}"
        )

    return source


def _actual_source_label(
    source: EvaluationRetrievedSource,
) -> str:
    source_name = (
        source.incident_code
        or source.document_title
    )

    return (
        f"#{source.rank} "
        f"{source_name} / "
        f"{source.section} "
        f"({source.similarity:.4f})"
    )


def load_golden_questions(
    path: Path = GOLDEN_SET_PATH,
) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Golden evaluation set was "
            f"not found: {path}"
        )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    questions = payload.get(
        "questions"
    )

    if not isinstance(
        questions,
        list,
    ):
        raise ValueError(
            "Golden evaluation file must "
            "contain a questions list."
        )

    if not (
        20
        <= len(questions)
        <= 30
    ):
        raise ValueError(
            "Evaluation set must contain "
            "between 20 and 30 questions."
        )

    for question in questions:
        if not question.get("id"):
            raise ValueError(
                "Every evaluation question "
                "must have an id."
            )

        if not question.get(
            "question"
        ):
            raise ValueError(
                "Every evaluation item "
                "must contain a question."
            )

        expected_sources = (
            question.get(
                "expected_sources"
            )
        )

        if not expected_sources:
            raise ValueError(
                f"{question['id']} has no "
                "expected sources."
            )

    return questions


def run_retrieval_evaluation(
    db: Session,
    *,
    top_k: int = 3,
) -> EvaluationSummary:
    if top_k != 3:
        raise ValueError(
            "M8 uses Top-3 retrieval "
            "success, so top_k must be 3."
        )

    questions = (
        load_golden_questions()
    )

    results: list[
        EvaluationQuestionResult
    ] = []

    for case in questions:
        question = (
            case["question"].strip()
        )

        started = perf_counter()

        retrieved = (
            retrieve_rag_evidence(
                db,
                question,
                service=(
                    case.get(
                        "service"
                    )
                ),
                severity=(
                    case.get(
                        "severity"
                    )
                ),
                date_from=None,
                date_to=None,
                section=None,
                top_k=top_k,
            )
        )

        duration_ms = (
            perf_counter()
            - started
        ) * 1000

        expected_sources = (
            case[
                "expected_sources"
            ]
        )

        passed = any(
            _source_matches(
                expected,
                actual,
            )
            for expected
            in expected_sources
            for actual
            in retrieved
        )

        retrieved_sources = [
            EvaluationRetrievedSource(
                rank=rank,
                chunk_id=item.chunk_id,
                incident_code=(
                    item.incident_code
                ),
                document_title=(
                    item.document_title
                ),
                section=item.section,
                similarity=(
                    item.similarity
                ),
            )
            for rank, item
            in enumerate(
                retrieved,
                start=1,
            )
        ]

        results.append(
            EvaluationQuestionResult(
                question_id=(
                    case["id"]
                ),
                question=question,
                passed=passed,
                expected_sources=[
                    _expected_source_label(
                        expected
                    )
                    for expected
                    in expected_sources
                ],
                retrieved_sources=(
                    retrieved_sources
                ),
                duration_ms=round(
                    duration_ms,
                    2,
                ),
            )
        )

    total = len(results)

    passed_count = sum(
        1
        for result in results
        if result.passed
    )

    failed_count = (
        total - passed_count
    )

    score_percent = (
        (
            passed_count
            / total
        )
        * 100
        if total
        else 0.0
    )

    average_retrieval_ms = (
        sum(
            result.duration_ms
            for result in results
        )
        / total
        if total
        else 0.0
    )

    summary = EvaluationSummary(
        metric=(
            "top_3_retrieval_success"
        ),
        top_k=3,
        total_questions=total,
        passed_questions=(
            passed_count
        ),
        failed_questions=(
            failed_count
        ),
        score_percent=round(
            score_percent,
            2,
        ),
        average_retrieval_ms=round(
            average_retrieval_ms,
            2,
        ),
        generated_at=datetime.now(
            timezone.utc
        ),
        results=results,
    )

    save_evaluation_results(
        summary
    )

    return summary


def save_evaluation_results(
    summary: EvaluationSummary,
) -> None:
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LATEST_JSON_PATH.write_text(
        summary.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    with LATEST_CSV_PATH.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "question_id",
                "question",
                "passed",
                "expected_sources",
                "top_1",
                "top_2",
                "top_3",
                "duration_ms",
            ],
        )

        writer.writeheader()

        for result in summary.results:
            retrieved = [
                _actual_source_label(
                    source
                )
                for source
                in result.retrieved_sources
            ]

            while len(retrieved) < 3:
                retrieved.append("")

            writer.writerow(
                {
                    "question_id":
                        result.question_id,

                    "question":
                        result.question,

                    "passed":
                        result.passed,

                    "expected_sources":
                        " | ".join(
                            result.expected_sources
                        ),

                    "top_1":
                        retrieved[0],

                    "top_2":
                        retrieved[1],

                    "top_3":
                        retrieved[2],

                    "duration_ms":
                        result.duration_ms,
                }
            )


def load_latest_evaluation(
) -> EvaluationSummary:
    if not LATEST_JSON_PATH.exists():
        raise FileNotFoundError(
            "No evaluation result exists yet."
        )

    return (
        EvaluationSummary
        .model_validate_json(
            LATEST_JSON_PATH
            .read_text(
                encoding="utf-8"
            )
        )
    )