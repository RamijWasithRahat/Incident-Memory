from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.incidents import IncidentCreate, IncidentRead, IncidentUpdate
from app.services.incidents import (
    IncidentCodeAlreadyExistsError,
    create_incident,
    delete_incident,
    get_incident,
    list_incidents,
    update_incident,
)

router = APIRouter(
    prefix="/api/incidents",
    tags=["incidents"],
)


@router.post(
    "",
    response_model=IncidentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_incident_endpoint(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_incident(db, payload)

    except IncidentCodeAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Incident code '{payload.incident_code}' already exists",
        ) from exc


@router.get(
    "",
    response_model=list[IncidentRead],
)
def list_incidents_endpoint(
    service: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return list_incidents(
        db,
        service=service,
        severity=severity,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{incident_id}",
    response_model=IncidentRead,
)
def get_incident_endpoint(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = get_incident(db, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident


@router.patch(
    "/{incident_id}",
    response_model=IncidentRead,
)
def update_incident_endpoint(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
):
    incident = get_incident(db, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    try:
        return update_incident(
            db,
            incident,
            payload,
        )

    except IncidentCodeAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Incident code already exists",
        ) from exc


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_incident_endpoint(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = get_incident(db, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    delete_incident(db, incident)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )