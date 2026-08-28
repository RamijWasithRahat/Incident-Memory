from datetime import date

from app.services.rag_service import (
    RetrievedEvidence,
    build_evidence_context,
    select_strong_evidence,
)


def test_build_evidence_context() -> None:
    evidence = [
        RetrievedEvidence(
            chunk_id=1,
            document_id=1,
            document_title=(
                "INC-012 - Payment API "
                "database timeout"
            ),
            document_type=(
                "incident_record"
            ),
            incident_id=1,
            incident_code="INC-012",
            section="root_cause",
            text=(
                "PostgreSQL connection pool "
                "was exhausted."
            ),
            service="payment-service",
            severity="SEV-2",
            incident_date=date(
                2026,
                6,
                15,
            ),
            similarity=0.82,
        ),
        RetrievedEvidence(
            chunk_id=2,
            document_id=1,
            document_title=(
                "INC-012 - Payment API "
                "database timeout"
            ),
            document_type=(
                "incident_record"
            ),
            incident_id=1,
            incident_code="INC-012",
            section="solution",
            text=(
                "Worker concurrency was reduced "
                "and pool capacity increased."
            ),
            service="payment-service",
            severity="SEV-2",
            incident_date=date(
                2026,
                6,
                15,
            ),
            similarity=0.79,
        ),
    ]

    context = build_evidence_context(
        evidence
    )

    assert "[S1]" in context
    assert "[S2]" in context
    assert "INC-012" in context
    assert "root_cause" in context
    assert "solution" in context


def test_generic_document_context() -> None:
    evidence = [
        RetrievedEvidence(
            chunk_id=10,
            document_id=4,
            document_title=(
                "Database Timeout Runbook"
            ),
            document_type="runbook",
            incident_id=None,
            incident_code=None,
            section="checks",
            text=(
                "Check active database "
                "connections and pool usage."
            ),
            service="database",
            severity=None,
            incident_date=None,
            similarity=0.75,
        ),
    ]

    context = build_evidence_context(
        evidence
    )

    assert (
        "Generic document/runbook"
        in context
    )

    assert (
        "Check active database "
        "connections and pool usage."
        in context
    )


def test_weak_evidence_is_removed() -> None:
    evidence = [
        RetrievedEvidence(
            chunk_id=1,
            document_id=1,
            document_title="Test",
            document_type="runbook",
            incident_id=None,
            incident_code=None,
            section="summary",
            text="Unrelated text.",
            service=None,
            severity=None,
            incident_date=None,
            similarity=0.10,
        ),
    ]

    strong = select_strong_evidence(
        evidence
    )

    assert strong == []