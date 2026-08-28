from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Document,
    DocumentChunk,
)
from app.services.embeddings import embed_query


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    document_id: int
    document_title: str
    original_filename: str
    section: str
    text: str
    service: str | None
    severity: str | None
    incident_date: date | None
    similarity: float


def search_chunks(
    db: Session,
    query: str,
    *,
    top_k: int = 5,
    service: str | None = None,
    section: str | None = None,
) -> list[RetrievedChunk]:
    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError(
            "Search query must not be empty."
        )

    if top_k < 1 or top_k > 50:
        raise ValueError(
            "top_k must be between 1 and 50."
        )

    query_embedding = embed_query(
        cleaned_query
    )

    cosine_distance = (
        DocumentChunk.embedding
        .cosine_distance(
            query_embedding
        )
        .label("cosine_distance")
    )

    statement = (
        select(
            DocumentChunk,
            Document,
            cosine_distance,
        )
        .join(
            Document,
            Document.id
            == DocumentChunk.document_id,
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

    if section:
        statement = statement.where(
            DocumentChunk.section
            == section.strip()
        )

    statement = (
        statement
        .order_by(cosine_distance)
        .limit(top_k)
    )

    rows = db.execute(
        statement
    ).all()

    results: list[RetrievedChunk] = []

    for (
        chunk,
        document,
        distance,
    ) in rows:
        similarity = (
            1.0 - float(distance)
        )

        results.append(
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=document.id,
                document_title=document.title,
                original_filename=(
                    document.original_filename
                ),
                section=chunk.section,
                text=chunk.chunk_text,
                service=chunk.service,
                severity=chunk.severity,
                incident_date=(
                    chunk.incident_date
                ),
                similarity=similarity,
            )
        )

    return results