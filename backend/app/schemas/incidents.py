from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IncidentBase(BaseModel):
    incident_code: str = Field(
        min_length=1,
        max_length=50,
    )

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    service: str = Field(
        min_length=1,
        max_length=100,
    )

    severity: str = Field(
        min_length=1,
        max_length=20,
    )

    incident_date: date

    symptoms: str = Field(min_length=1)

    root_cause: str = Field(min_length=1)

    solution: str = Field(min_length=1)

    notes: str | None = None

    @field_validator(
        "incident_code",
        "title",
        "service",
        "severity",
        "symptoms",
        "root_cause",
        "solution",
    )
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("must not be blank")

        return value

    @field_validator("notes")
    @classmethod
    def strip_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        return value or None


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    incident_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    service: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    severity: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    incident_date: date | None = None

    symptoms: str | None = Field(
        default=None,
        min_length=1,
    )

    root_cause: str | None = Field(
        default=None,
        min_length=1,
    )

    solution: str | None = Field(
        default=None,
        min_length=1,
    )

    notes: str | None = None


class IncidentRead(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime