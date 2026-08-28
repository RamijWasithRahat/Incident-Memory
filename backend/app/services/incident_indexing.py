from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Document,
    DocumentChunk,
    Incident,
)
from app.services.embeddings import embed_texts


INCIDENT_DOCUMENT_TYPE = "incident_record"


def _build_incident_sections(
    incident: Incident,
) -> list[tuple[str, str, str]]:
    """
    Build searchable sections for one structured incident.

    Each tuple contains:
    (
        section_name,
        text_saved_in_database,
        text_used_for_embedding,
    )
    """

    sections: list[tuple[str, str, str]] = []

    summary_text = (
        f"{incident.incident_code} - {incident.title}\n"
        f"Service: {incident.service}\n"
        f"Severity: {incident.severity}\n"
        f"Date: {incident.incident_date.isoformat()}"
    )

    sections.append(
        (
            "summary",
            summary_text,
            summary_text,
        )
    )

    structured_sections = [
        (
            "symptoms",
            "Symptoms",
            incident.symptoms,
        ),
        (
            "root_cause",
            "Root Cause",
            incident.root_cause,
        ),
        (
            "solution",
            "Solution",
            incident.solution,
        ),
    ]

    if incident.notes:
        structured_sections.append(
            (
                "notes",
                "Notes",
                incident.notes,
            )
        )

    for (
        section_name,
        section_label,
        section_text,
    ) in structured_sections:
        searchable_text = (
            f"Incident: {incident.incident_code} - "
            f"{incident.title}\n"
            f"Service: {incident.service}\n"
            f"Severity: {incident.severity}\n"
            f"Section: {section_label}\n"
            f"{section_text}"
        )

        sections.append(
            (
                section_name,
                section_text,
                searchable_text,
            )
        )

    return sections


def index_incident(
    db: Session,
    incident: Incident,
) -> Document:
    """
    Create or rebuild the vector index for one incident.

    Existing automatically generated incident index
    documents are removed before the new one is created.
    """

    if incident.id is None:
        raise ValueError(
            "Incident must be saved before indexing."
        )

    existing_documents = list(
        db.scalars(
            select(Document).where(
                Document.incident_id == incident.id,
                Document.document_type
                == INCIDENT_DOCUMENT_TYPE,
            )
        ).all()
    )

    for document in existing_documents:
        db.delete(document)

    if existing_documents:
        db.flush()

    sections = _build_incident_sections(
        incident
    )

    embedding_inputs = [
        embedding_text
        for (
            _section,
            _stored_text,
            embedding_text,
        ) in sections
    ]

    embeddings = embed_texts(
        embedding_inputs
    )

    if len(embeddings) != len(sections):
        raise RuntimeError(
            "Embedding count does not match "
            "incident section count."
        )

    document = Document(
        incident_id=incident.id,
        title=(
            f"{incident.incident_code} - "
            f"{incident.title}"
        ),
        document_type=INCIDENT_DOCUMENT_TYPE,
        original_filename=(
            f"{incident.incident_code}.incident"
        ),
        service=incident.service,
    )

    db.add(document)
    db.flush()

    for chunk_index, (
        section_data,
        embedding,
    ) in enumerate(
        zip(
            sections,
            embeddings,
        )
    ):
        (
            section_name,
            stored_text,
            _embedding_text,
        ) = section_data

        chunk = DocumentChunk(
            document_id=document.id,
            section=section_name,
            chunk_index=chunk_index,
            chunk_text=stored_text,
            service=incident.service,
            severity=incident.severity,
            incident_date=incident.incident_date,
            embedding=embedding,
        )

        db.add(chunk)

    db.flush()

    return document