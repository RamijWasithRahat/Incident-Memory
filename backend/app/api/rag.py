from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.rag import (
    RAGAskRequest,
    RAGAskResponse,
)
from app.services.llm import LocalLLMError
from app.services.rag_service import (
    answer_rag_question,
)


router = APIRouter(
    prefix="/api/rag",
    tags=["rag"],
)


@router.post(
    "/ask",
    response_model=RAGAskResponse,
)
def ask_rag_question(
    payload: RAGAskRequest,
    db: Session = Depends(get_db),
) -> RAGAskResponse:
    try:
        return answer_rag_question(
            db,
            payload.question,
            service=payload.service,
            severity=payload.severity,
            section=payload.section,
            date_from=payload.date_from,
            date_to=payload.date_to,
            top_k=payload.top_k,
        )

    except LocalLLMError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(exc),
        ) from exc