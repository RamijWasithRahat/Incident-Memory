from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.evaluation import (
    EvaluationSummary,
)
from app.services.evaluation import (
    load_latest_evaluation,
    run_retrieval_evaluation,
)


router = APIRouter(
    prefix="/api/evaluation",
    tags=["evaluation"],
)


@router.post(
    "/run",
    response_model=EvaluationSummary,
)
def run_evaluation(
    db: Session = Depends(
        get_db
    ),
) -> EvaluationSummary:
    try:
        return (
            run_retrieval_evaluation(
                db,
                top_k=3,
            )
        )

    except (
        FileNotFoundError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        ) from exc


@router.get(
    "/results",
    response_model=EvaluationSummary,
)
def get_evaluation_results(
) -> EvaluationSummary:
    try:
        return (
            load_latest_evaluation()
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc