import json

from datetime import date

from app.services.evaluation import (
    GOLDEN_SET_PATH,
    _source_matches,
    load_golden_questions,
)

from app.services.rag_service import (
    RetrievedEvidence,
)


def make_evidence(
    *,
    incident_code: str | None,
    document_title: str,
    section: str,
) -> RetrievedEvidence:
    return RetrievedEvidence(
        chunk_id=1,
        document_id=1,

        document_title=(
            document_title
        ),

        document_type=(
            "incident_record"
        ),

        incident_id=(
            1
            if incident_code
            else None
        ),

        incident_code=(
            incident_code
        ),

        section=section,

        text=(
            "Test evidence."
        ),

        service=(
            "test-service"
        ),

        severity="SEV-2",

        incident_date=date(
            2026,
            8,
            28,
        ),

        similarity=0.8,
    )


def test_golden_set_has_20_to_30_questions(
) -> None:
    questions = (
        load_golden_questions()
    )

    assert (
        20
        <= len(questions)
        <= 30
    )


def test_golden_question_ids_are_unique(
) -> None:
    payload = json.loads(
        GOLDEN_SET_PATH.read_text(
            encoding="utf-8"
        )
    )

    ids = [
        item["id"]
        for item
        in payload["questions"]
    ]

    assert (
        len(ids)
        == len(set(ids))
    )


def test_incident_source_match(
) -> None:
    evidence = make_evidence(
        incident_code="INC-012",

        document_title=(
            "INC-012 - Payment "
            "API database timeout"
        ),

        section="root_cause",
    )

    expected = {
        "incident_code":
            "INC-012",

        "section":
            "root_cause",
    }

    assert (
        _source_matches(
            expected,
            evidence,
        )
        is True
    )


def test_incident_wrong_section_does_not_match(
) -> None:
    evidence = make_evidence(
        incident_code="INC-012",

        document_title=(
            "INC-012 - Payment "
            "API database timeout"
        ),

        section="symptoms",
    )

    expected = {
        "incident_code":
            "INC-012",

        "section":
            "root_cause",
    }

    assert (
        _source_matches(
            expected,
            evidence,
        )
        is False
    )


def test_runbook_title_and_section_match(
) -> None:
    evidence = make_evidence(
        incident_code=None,

        document_title=(
            "Database Timeout Runbook"
        ),

        section="checks",
    )

    expected = {
        "document_title_contains":
            "Database Timeout Runbook",

        "section":
            "checks",
    }

    assert (
        _source_matches(
            expected,
            evidence,
        )
        is True
    )