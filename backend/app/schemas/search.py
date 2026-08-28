from datetime import date
from typing import Self

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)


class SimilarIncidentSearchRequest(
    BaseModel
):
    problem_description: str = Field(
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

    date_from: date | None = None
    date_to: date | None = None

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    @field_validator(
        "problem_description"
    )
    @classmethod
    def clean_problem_description(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Problem description "
                "must not be blank."
            )

        return value

    @field_validator(
        "service",
        "severity",
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

    @model_validator(
        mode="after"
    )
    def validate_date_range(
        self,
    ) -> Self:
        if (
            self.date_from is not None
            and self.date_to is not None
            and self.date_from
            > self.date_to
        ):
            raise ValueError(
                "date_from must be "
                "before or equal to date_to."
            )

        return self


class SimilarIncidentEvidence(
    BaseModel
):
    chunk_id: int
    section: str
    text: str
    similarity: float


class SimilarIncidentResult(
    BaseModel
):
    incident_id: int
    incident_code: str
    title: str
    service: str
    severity: str
    incident_date: date

    symptoms: str
    root_cause: str
    solution: str
    notes: str | None

    similarity: float

    evidence: list[
        SimilarIncidentEvidence
    ]


class SimilarIncidentSearchResponse(
    BaseModel
):
    problem_description: str
    count: int
    results: list[
        SimilarIncidentResult
    ]