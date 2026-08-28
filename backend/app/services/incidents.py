from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Incident
from app.schemas.incidents import (
    IncidentCreate,
    IncidentUpdate,
)
from app.services.incident_indexing import (
    index_incident,
)


class IncidentCodeAlreadyExistsError(
    Exception
):
    pass


def create_incident(
    db: Session,
    payload: IncidentCreate,
) -> Incident:
    incident = Incident(
        **payload.model_dump()
    )

    db.add(incident)

    try:
        # Obtain the incident ID without committing.
        db.flush()

        # M5:
        # Immediately create searchable incident
        # sections and embeddings.
        index_incident(
            db,
            incident,
        )

        # Incident + vector index are committed
        # together.
        db.commit()

    except IntegrityError as exc:
        db.rollback()

        raise IncidentCodeAlreadyExistsError(
            payload.incident_code
        ) from exc

    except Exception:
        db.rollback()
        raise

    db.refresh(incident)

    return incident


def list_incidents(
    db: Session,
    *,
    service: str | None = None,
    severity: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Incident]:
    statement = select(
        Incident
    ).order_by(
        Incident.incident_date.desc(),
        Incident.id.desc(),
    )

    if service:
        statement = statement.where(
            Incident.service == service
        )

    if severity:
        statement = statement.where(
            Incident.severity == severity
        )

    statement = (
        statement
        .offset(skip)
        .limit(limit)
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


def get_incident(
    db: Session,
    incident_id: int,
) -> Incident | None:
    return db.get(
        Incident,
        incident_id,
    )


def update_incident(
    db: Session,
    incident: Incident,
    payload: IncidentUpdate,
) -> Incident:
    changes = payload.model_dump(
        exclude_unset=True
    )

    for field, value in changes.items():
        setattr(
            incident,
            field,
            value,
        )

    try:
        # Validate pending DB changes before rebuilding
        # the searchable incident representation.
        db.flush()

        # Rebuild the index because symptoms,
        # root cause, solution, service, etc.
        # may have changed.
        index_incident(
            db,
            incident,
        )

        db.commit()

    except IntegrityError as exc:
        db.rollback()

        raise IncidentCodeAlreadyExistsError(
            changes.get(
                "incident_code",
                incident.incident_code,
            )
        ) from exc

    except Exception:
        db.rollback()
        raise

    db.refresh(incident)

    return incident


def delete_incident(
    db: Session,
    incident: Incident,
) -> None:
    db.delete(incident)
    db.commit()