from io import BytesIO

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.models import (
    Document,
    DocumentChunk,
)
from app.db.session import SessionLocal
from app.main import app


client = TestClient(app)


def test_markdown_upload_creates_chunks() -> None:
    content = b"""
## Symptoms

Database timeout errors.

## Root Cause

Connection pool exhaustion.

## Resolution

Increase connection pool capacity.
"""

    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "test_runbook.md",
                BytesIO(content),
                "text/markdown",
            )
        },
        data={
            "title": "Test DB Runbook",
            "document_type": "runbook",
            "service": "test-service",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["chunk_count"] >= 3

    assert "symptoms" in body["sections"]
    assert "root_cause" in body["sections"]
    assert "resolution" in body["sections"]

    document_id = body["id"]

    with SessionLocal() as db:
        db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id
                == document_id
            )
        )

        db.execute(
            delete(Document).where(
                Document.id == document_id
            )
        )

        db.commit()


def test_unsupported_file_is_rejected() -> None:
    response = client.post(
        "/api/documents/upload",
        files={
            "file": (
                "invalid.pdf",
                BytesIO(b"fake pdf"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 415