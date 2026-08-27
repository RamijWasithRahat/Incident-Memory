from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.documents import (
    DocumentUploadResponse,
)

from app.services.ingestion import (
    DocumentTooLargeError,
    InvalidDocumentContentError,
    RelatedIncidentNotFoundError,
    UnsupportedDocumentTypeError,
    decode_document,
    ingest_document,
)


router = APIRouter(
    prefix="/api/documents",
    tags=["documents"],
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    document_type: str = Form(
        default="runbook"
    ),
    incident_id: int | None = Form(
        default=None
    ),
    service: str | None = Form(
        default=None
    ),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:

    filename = file.filename

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    raw_data = await file.read()

    try:
        text = decode_document(
            filename,
            raw_data,
        )

    except UnsupportedDocumentTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc

    except DocumentTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc

    except InvalidDocumentContentError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    resolved_title = (
        title.strip()
        if title and title.strip()
        else Path(filename).stem
    )

    resolved_document_type = (
        document_type.strip()
        or "runbook"
    )

    resolved_service = (
        service.strip()
        if service and service.strip()
        else None
    )

    try:
        document, chunks = ingest_document(
            db,
            title=resolved_title,
            document_type=resolved_document_type,
            original_filename=filename,
            text=text,
            incident_id=incident_id,
            service=resolved_service,
        )

    except RelatedIncidentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    sections = list(
        dict.fromkeys(
            chunk.section
            for chunk in chunks
        )
    )

    return DocumentUploadResponse(
        id=document.id,
        title=document.title,
        document_type=document.document_type,
        original_filename=document.original_filename,
        incident_id=document.incident_id,
        service=document.service,
        chunk_count=len(chunks),
        sections=sections,
        created_at=document.created_at,
    )