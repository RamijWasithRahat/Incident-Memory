from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Incident
from app.schemas.incidents import IncidentCreate, IncidentUpdate


class IncidentCodeAlreadyExistsError(Exception):
    pass


def create_incident(
    db: Session,
    payload: IncidentCreate,
) -> Incident:
    incident = Incident(**payload.model_dump())

    db.add(incident)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise IncidentCodeAlreadyExistsError(
            payload.incident_code
        ) from exc

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

    statement = select(Incident).order_by(
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

    statement = statement.offset(skip).limit(limit)

    return list(db.scalars(statement).all())


def get_incident(
    db: Session,
    incident_id: int,
) -> Incident | None:

    return db.get(Incident, incident_id)


def update_incident(
    db: Session,
    incident: Incident,
    payload: IncidentUpdate,
) -> Incident:

    changes = payload.model_dump(
        exclude_unset=True
    )

    for field, value in changes.items():
        setattr(incident, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        raise IncidentCodeAlreadyExistsError(
            changes.get(
                "incident_code",
                incident.incident_code,
            )
        ) from exc

    db.refresh(incident)

    return incident


def delete_incident(
    db: Session,
    incident: Incident,
) -> None:

    db.delete(incident)
    db.commit()