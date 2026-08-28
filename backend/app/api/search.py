from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.search import (
    SimilarIncidentSearchRequest,
    SimilarIncidentSearchResponse,
)
from app.services.similar_incidents import (
    find_similar_incidents,
)


router = APIRouter(
    prefix="/api/search",
    tags=["search"],
)


@router.post(
    "/similar",
    response_model=(
        SimilarIncidentSearchResponse
    ),
)
def search_similar_incidents(
    payload: SimilarIncidentSearchRequest,
    db: Session = Depends(
        get_db
    ),
) -> SimilarIncidentSearchResponse:
    results = find_similar_incidents(
        db,
        payload.problem_description,
        service=payload.service,
        severity=payload.severity,
        date_from=payload.date_from,
        date_to=payload.date_to,
        top_k=payload.top_k,
    )

    return SimilarIncidentSearchResponse(
        problem_description=(
            payload.problem_description
        ),
        count=len(results),
        results=results,
    )