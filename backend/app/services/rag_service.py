from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import (
    Document,
    DocumentChunk,
    Incident,
)
from app.schemas.rag import (
    RAGAskResponse,
    RAGSource,
)
from app.services.embeddings import embed_query
from app.services.llm import (
    INSUFFICIENT_EVIDENCE_MESSAGE,
    generate_grounded_answer,
)


@dataclass(frozen=True)
class RetrievedEvidence:
    chunk_id: int
    document_id: int

    document_title: str
    document_type: str

    incident_id: int | None
    incident_code: str | None

    section: str
    text: str

    service: str | None
    severity: str | None
    incident_date: date | None

    similarity: float


def _similarity_from_distance(
    distance: float,
) -> float:
    similarity = 1.0 - float(distance)

    similarity = max(
        -1.0,
        min(
            1.0,
            similarity,
        ),
    )

    return round(
        similarity,
        4,
    )


def retrieve_rag_evidence(
    db: Session,
    question: str,
    *,
    service: str | None = None,
    severity: str | None = None,
    section: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    top_k: int | None = None,
) -> list[RetrievedEvidence]:
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError(
            "Question must not be empty."
        )

    effective_top_k = (
        top_k
        if top_k is not None
        else settings.rag_top_k
    )

    if (
        effective_top_k < 1
        or effective_top_k > 10
    ):
        raise ValueError(
            "top_k must be between 1 and 10."
        )

    query_embedding = embed_query(
        cleaned_question
    )

    cosine_distance = (
        DocumentChunk.embedding
        .cosine_distance(
            query_embedding
        )
        .label(
            "cosine_distance"
        )
    )

    statement = (
        select(
            DocumentChunk,
            Document,
            Incident,
            cosine_distance,
        )
        .join(
            Document,
            Document.id
            == DocumentChunk.document_id,
        )
        .outerjoin(
            Incident,
            Incident.id
            == Document.incident_id,
        )
        .where(
            DocumentChunk.embedding.is_not(
                None
            )
        )
    )

    if service:
        statement = statement.where(
            DocumentChunk.service
            == service.strip()
        )

    if severity:
        statement = statement.where(
            DocumentChunk.severity
            == severity.strip()
        )

    if section:
        statement = statement.where(
            DocumentChunk.section
            == section.strip()
        )

    if date_from:
        statement = statement.where(
            DocumentChunk.incident_date
            >= date_from
        )

    if date_to:
        statement = statement.where(
            DocumentChunk.incident_date
            <= date_to
        )

    statement = (
        statement
        .order_by(
            cosine_distance
        )
        .limit(
            effective_top_k
        )
    )

    rows = db.execute(
        statement
    ).all()

    evidence: list[
        RetrievedEvidence
    ] = []

    for (
        chunk,
        document,
        incident,
        distance,
    ) in rows:
        evidence.append(
            RetrievedEvidence(
                chunk_id=chunk.id,
                document_id=document.id,
                document_title=(
                    document.title
                ),
                document_type=(
                    document.document_type
                ),
                incident_id=(
                    incident.id
                    if incident
                    else None
                ),
                incident_code=(
                    incident.incident_code
                    if incident
                    else None
                ),
                section=chunk.section,
                text=chunk.chunk_text,
                service=chunk.service,
                severity=chunk.severity,
                incident_date=(
                    chunk.incident_date
                ),
                similarity=(
                    _similarity_from_distance(
                        distance
                    )
                ),
            )
        )

    return evidence


def select_strong_evidence(
    evidence: list[RetrievedEvidence],
) -> list[RetrievedEvidence]:
    return [
        item
        for item in evidence
        if (
            item.similarity
            >= settings.rag_min_similarity
        )
    ]


def build_evidence_context(
    evidence: list[RetrievedEvidence],
) -> str:
    blocks: list[str] = []

    total_characters = 0

    for index, item in enumerate(
        evidence,
        start=1,
    ):
        source_id = f"S{index}"

        incident_label = (
            item.incident_code
            if item.incident_code
            else "Generic document/runbook"
        )

        block = (
            f"[{source_id}]\n"
            f"Incident: {incident_label}\n"
            f"Document: {item.document_title}\n"
            f"Document Type: "
            f"{item.document_type}\n"
            f"Section: {item.section}\n"
            f"Service: {item.service}\n"
            f"Severity: {item.severity}\n"
            f"Incident Date: "
            f"{item.incident_date}\n"
            f"Similarity: "
            f"{item.similarity:.4f}\n"
            "Evidence:\n"
            f"{item.text}\n"
        )

        if (
            total_characters
            + len(block)
            > settings.rag_max_context_chars
        ):
            break

        blocks.append(
            block
        )

        total_characters += len(
            block
        )

    return "\n---\n".join(
        blocks
    )


def build_sources(
    evidence: list[RetrievedEvidence],
) -> list[RAGSource]:
    sources: list[RAGSource] = []

    for index, item in enumerate(
        evidence,
        start=1,
    ):
        sources.append(
            RAGSource(
                source_id=f"S{index}",
                chunk_id=item.chunk_id,
                document_id=item.document_id,
                document_title=(
                    item.document_title
                ),
                document_type=(
                    item.document_type
                ),
                incident_id=(
                    item.incident_id
                ),
                incident_code=(
                    item.incident_code
                ),
                section=item.section,
                service=item.service,
                severity=item.severity,
                incident_date=(
                    item.incident_date
                ),
                similarity=(
                    item.similarity
                ),
                text=item.text,
            )
        )

    return sources


def answer_rag_question(
    db: Session,
    question: str,
    *,
    service: str | None = None,
    severity: str | None = None,
    section: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    top_k: int | None = None,
) -> RAGAskResponse:
    retrieved = retrieve_rag_evidence(
        db,
        question,
        service=service,
        severity=severity,
        section=section,
        date_from=date_from,
        date_to=date_to,
        top_k=top_k,
    )

    strong_evidence = (
        select_strong_evidence(
            retrieved
        )
    )

    if not strong_evidence:
        return RAGAskResponse(
            question=question,
            answer=(
                INSUFFICIENT_EVIDENCE_MESSAGE
            ),
            insufficient_evidence=True,
            model=None,
            evidence_count=0,
            sources=[],
        )

    evidence_context = (
        build_evidence_context(
            strong_evidence
        )
    )

    answer = generate_grounded_answer(
        question=question,
        evidence_context=(
            evidence_context
        ),
    )

    sources = build_sources(
        strong_evidence
    )

    return RAGAskResponse(
        question=question,
        answer=answer,
        insufficient_evidence=False,
        model=settings.llm_model,
        evidence_count=len(
            strong_evidence
        ),
        sources=sources,
    )