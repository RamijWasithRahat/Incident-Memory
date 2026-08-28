from datetime import date
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)


class RAGAskRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
    )

    service: str | None = Field(
        default=None,
        max_length=100,
    )

    severity: str | None = Field(
        default=None,
        max_length=20,
    )

    section: str | None = Field(
        default=None,
        max_length=100,
    )

    date_from: date | None = None
    date_to: date | None = None

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    @field_validator("question")
    @classmethod
    def clean_question(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Question must not be blank."
            )

        return value

    @field_validator(
        "service",
        "severity",
        "section",
    )
    @classmethod
    def clean_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None

    @model_validator(mode="after")
    def validate_date_range(
        self,
    ) -> Self:
        if (
            self.date_from is not None
            and self.date_to is not None
            and self.date_from > self.date_to
        ):
            raise ValueError(
                "date_from must be before "
                "or equal to date_to."
            )

        return self


class RAGSource(BaseModel):
    source_id: str

    chunk_id: int
    document_id: int

    document_title: str
    document_type: str

    incident_id: int | None = None
    incident_code: str | None = None

    section: str

    service: str | None = None
    severity: str | None = None
    incident_date: date | None = None

    similarity: float

    text: str


class RAGAskResponse(BaseModel):
    question: str
    answer: str

    insufficient_evidence: bool

    model: str | None = None

    evidence_count: int

    sources: list[RAGSource]