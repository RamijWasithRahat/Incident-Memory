from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import (
    Document,
    DocumentChunk,
    Incident,
)
from app.services.document_parser import (
    TextChunk,
    chunk_sections,
    parse_sections,
)
from app.services.embeddings import embed_texts


MAX_UPLOAD_BYTES = 2 * 1024 * 1024

SUPPORTED_EXTENSIONS = {
    ".txt": "text",
    ".md": "markdown",
}


class DocumentIngestionError(Exception):
    pass


class UnsupportedDocumentTypeError(
    DocumentIngestionError
):
    pass


class DocumentTooLargeError(
    DocumentIngestionError
):
    pass


class InvalidDocumentContentError(
    DocumentIngestionError
):
    pass


class RelatedIncidentNotFoundError(
    DocumentIngestionError
):
    pass


def decode_document(
    filename: str,
    raw_data: bytes,
) -> str:
    suffix = Path(
        filename
    ).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentTypeError(
            "Only .txt and .md files are supported."
        )

    if not raw_data:
        raise InvalidDocumentContentError(
            "Uploaded file is empty."
        )

    if len(raw_data) > MAX_UPLOAD_BYTES:
        raise DocumentTooLargeError(
            "Maximum upload size is 2 MB."
        )

    try:
        text = raw_data.decode(
            "utf-8-sig"
        )

    except UnicodeDecodeError as exc:
        raise InvalidDocumentContentError(
            "Document must use UTF-8 text encoding."
        ) from exc

    if not text.strip():
        raise InvalidDocumentContentError(
            "Document contains no searchable text."
        )

    return text


def ingest_document(
    db: Session,
    *,
    title: str,
    document_type: str,
    original_filename: str,
    text: str,
    incident_id: int | None = None,
    service: str | None = None,
) -> tuple[Document, list[TextChunk]]:
    related_incident = None

    if incident_id is not None:
        related_incident = db.get(
            Incident,
            incident_id,
        )

        if related_incident is None:
            raise RelatedIncidentNotFoundError(
                "Related incident was not found."
            )

    effective_service = (
        service
        or (
            related_incident.service
            if related_incident
            else None
        )
    )

    severity = (
        related_incident.severity
        if related_incident
        else None
    )

    incident_date = (
        related_incident.incident_date
        if related_incident
        else None
    )

    sections = parse_sections(text)

    chunks = chunk_sections(
        sections
    )

    if not chunks:
        raise InvalidDocumentContentError(
            "No searchable chunks could be created."
        )

    # M4:
    # Generate an embedding for every document chunk.
    chunk_embeddings = embed_texts(
        [
            chunk.text
            for chunk in chunks
        ]
    )

    if len(chunk_embeddings) != len(chunks):
        raise RuntimeError(
            "Embedding count does not match "
            "document chunk count."
        )

    document = Document(
        incident_id=incident_id,
        title=title,
        document_type=document_type,
        original_filename=original_filename,
        service=effective_service,
    )

    db.add(document)

    try:
        db.flush()

        for chunk, embedding in zip(
            chunks,
            chunk_embeddings,
        ):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    section=chunk.section,
                    chunk_index=chunk.chunk_index,
                    chunk_text=chunk.text,
                    service=effective_service,
                    severity=severity,
                    incident_date=incident_date,
                    embedding=embedding,
                )
            )

        db.commit()
        db.refresh(document)

    except Exception:
        db.rollback()
        raise

    return document, chunks