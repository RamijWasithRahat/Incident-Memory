from fastapi.testclient import TestClient
from sqlalchemy import (
    func,
    select,
)

from app.db.models import (
    Document,
    DocumentChunk,
)
from app.db.session import SessionLocal
from app.main import app
from app.services.incident_indexing import (
    INCIDENT_DOCUMENT_TYPE,
)


client = TestClient(app)


def _create_incident(
    payload: dict,
) -> dict:
    response = client.post(
        "/api/incidents",
        json=payload,
    )

    assert (
        response.status_code
        == 201
    )

    return response.json()


def _delete_incident(
    incident_id: int,
) -> None:
    client.delete(
        f"/api/incidents/{incident_id}"
    )


def test_similar_incident_search_returns_relevant_incident() -> None:
    database_incident = None
    redis_incident = None

    try:
        database_incident = (
            _create_incident(
                {
                    "incident_code": (
                        "TEST-M5-DB"
                    ),
                    "title": (
                        "Payment database "
                        "connection timeout"
                    ),
                    "service": (
                        "m5-test-service"
                    ),
                    "severity": "SEV-2",
                    "incident_date": (
                        "2026-08-20"
                    ),
                    "symptoms": (
                        "Payment requests became "
                        "slow after deployment and "
                        "PostgreSQL connection "
                        "timeouts increased."
                    ),
                    "root_cause": (
                        "PostgreSQL connection "
                        "pool exhaustion after "
                        "worker concurrency "
                        "increased."
                    ),
                    "solution": (
                        "Reduced worker count "
                        "and increased database "
                        "pool capacity."
                    ),
                    "notes": None,
                }
            )
        )

        redis_incident = (
            _create_incident(
                {
                    "incident_code": (
                        "TEST-M5-REDIS"
                    ),
                    "title": (
                        "Redis memory "
                        "exhaustion"
                    ),
                    "service": (
                        "m5-test-service"
                    ),
                    "severity": "SEV-2",
                    "incident_date": (
                        "2026-08-21"
                    ),
                    "symptoms": (
                        "Cache writes failed "
                        "and Redis memory usage "
                        "reached its limit."
                    ),
                    "root_cause": (
                        "Redis memory was "
                        "exhausted by oversized "
                        "cached objects."
                    ),
                    "solution": (
                        "Removed stale cache "
                        "entries and adjusted "
                        "memory policies."
                    ),
                    "notes": None,
                }
            )
        )

        response = client.post(
            "/api/search/similar",
            json={
                "problem_description": (
                    "Payment requests became "
                    "slow after deployment and "
                    "database connections are "
                    "timing out."
                ),
                "service": (
                    "m5-test-service"
                ),
                "top_k": 2,
            },
        )

        assert (
            response.status_code
            == 200
        )

        body = response.json()

        assert body["count"] >= 1
        assert body["results"]

        first_result = (
            body["results"][0]
        )

        assert (
            first_result[
                "incident_code"
            ]
            == "TEST-M5-DB"
        )

        assert (
            first_result[
                "similarity"
            ]
            <= 1.0
        )

        assert (
            len(
                first_result[
                    "evidence"
                ]
            )
            >= 1
        )

    finally:
        if database_incident:
            _delete_incident(
                database_incident["id"]
            )

        if redis_incident:
            _delete_incident(
                redis_incident["id"]
            )


def test_deleting_incident_removes_generated_index() -> None:
    incident = None

    try:
        incident = _create_incident(
            {
                "incident_code": (
                    "TEST-M5-DELETE"
                ),
                "title": (
                    "Temporary indexed incident"
                ),
                "service": (
                    "m5-delete-service"
                ),
                "severity": "SEV-3",
                "incident_date": (
                    "2026-08-22"
                ),
                "symptoms": (
                    "Temporary timeout."
                ),
                "root_cause": (
                    "Temporary database issue."
                ),
                "solution": (
                    "Temporary fix."
                ),
                "notes": None,
            }
        )

        incident_id = incident["id"]

        with SessionLocal() as db:
            document_ids = list(
                db.scalars(
                    select(
                        Document.id
                    ).where(
                        Document.incident_id
                        == incident_id,
                        Document.document_type
                        == INCIDENT_DOCUMENT_TYPE,
                    )
                ).all()
            )

            assert document_ids

            chunk_count = db.scalar(
                select(
                    func.count()
                )
                .select_from(
                    DocumentChunk
                )
                .where(
                    DocumentChunk.document_id.in_(
                        document_ids
                    )
                )
            )

            assert chunk_count > 0

        response = client.delete(
            f"/api/incidents/{incident_id}"
        )

        assert (
            response.status_code
            == 204
        )

        incident = None

        with SessionLocal() as db:
            remaining_documents = (
                db.scalar(
                    select(
                        func.count()
                    )
                    .select_from(
                        Document
                    )
                    .where(
                        Document.id.in_(
                            document_ids
                        )
                    )
                )
            )

            remaining_chunks = (
                db.scalar(
                    select(
                        func.count()
                    )
                    .select_from(
                        DocumentChunk
                    )
                    .where(
                        DocumentChunk.document_id.in_(
                            document_ids
                        )
                    )
                )
            )

            assert (
                remaining_documents
                == 0
            )

            assert (
                remaining_chunks
                == 0
            )

    finally:
        if incident:
            _delete_incident(
                incident["id"]
            )