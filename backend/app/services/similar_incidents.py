from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Document,
    DocumentChunk,
    Incident,
)
from app.schemas.search import (
    SimilarIncidentEvidence,
    SimilarIncidentResult,
)
from app.services.embeddings import (
    embed_query,
)
from app.services.incident_indexing import (
    INCIDENT_DOCUMENT_TYPE,
)


def _cosine_similarity_from_distance(
    distance: float,
) -> float:
    similarity = (
        1.0 - float(distance)
    )

    # Cosine similarity theoretically ranges
    # from -1 to 1.
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


def find_similar_incidents(
    db: Session,
    problem_description: str,
    *,
    service: str | None = None,
    severity: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    top_k: int = 5,
) -> list[SimilarIncidentResult]:
    cleaned_problem = (
        problem_description.strip()
    )

    if not cleaned_problem:
        raise ValueError(
            "Problem description "
            "must not be empty."
        )

    if top_k < 1 or top_k > 20:
        raise ValueError(
            "top_k must be between "
            "1 and 20."
        )

    query_embedding = embed_query(
        cleaned_problem
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
            Incident,
            DocumentChunk,
            cosine_distance,
        )
        .join(
            Document,
            Document.incident_id
            == Incident.id,
        )
        .join(
            DocumentChunk,
            DocumentChunk.document_id
            == Document.id,
        )
        .where(
            Document.document_type
            == INCIDENT_DOCUMENT_TYPE,
            DocumentChunk.embedding.is_not(
                None
            ),
        )
    )

    # Metadata filters are applied before
    # ranking whenever the user supplies them.
    if service:
        statement = statement.where(
            Incident.service
            == service.strip()
        )

    if severity:
        statement = statement.where(
            Incident.severity
            == severity.strip()
        )

    if date_from:
        statement = statement.where(
            Incident.incident_date
            >= date_from
        )

    if date_to:
        statement = statement.where(
            Incident.incident_date
            <= date_to
        )

    # Retrieve more chunks than the requested
    # number of incidents because several high
    # ranking chunks may belong to the same
    # incident.
    candidate_limit = min(
        max(
            top_k * 20,
            50,
        ),
        500,
    )

    statement = (
        statement
        .order_by(
            cosine_distance
        )
        .limit(
            candidate_limit
        )
    )

    rows = db.execute(
        statement
    ).all()

    grouped: dict[
        int,
        SimilarIncidentResult,
    ] = {}

    for (
        incident,
        chunk,
        distance,
    ) in rows:
        similarity = (
            _cosine_similarity_from_distance(
                distance
            )
        )

        evidence = (
            SimilarIncidentEvidence(
                chunk_id=chunk.id,
                section=chunk.section,
                text=chunk.chunk_text,
                similarity=similarity,
            )
        )

        current = grouped.get(
            incident.id
        )

        if current is None:
            grouped[
                incident.id
            ] = SimilarIncidentResult(
                incident_id=incident.id,
                incident_code=(
                    incident.incident_code
                ),
                title=incident.title,
                service=incident.service,
                severity=incident.severity,
                incident_date=(
                    incident.incident_date
                ),
                symptoms=incident.symptoms,
                root_cause=(
                    incident.root_cause
                ),
                solution=incident.solution,
                notes=incident.notes,
                similarity=similarity,
                evidence=[
                    evidence
                ],
            )

            continue

        if (
            similarity
            > current.similarity
        ):
            current.similarity = (
                similarity
            )

        # Keep only the best few evidence
        # sections for each incident.
        if len(
            current.evidence
        ) < 3:
            current.evidence.append(
                evidence
            )

    results = sorted(
        grouped.values(),
        key=lambda result: (
            result.similarity,
            result.incident_date,
        ),
        reverse=True,
    )

    return results[:top_k]