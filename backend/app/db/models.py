from datetime import date, datetime

from sqlalchemy import Date, DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Incident(Base):
    __tablename__ = "incidents"

    __table_args__ = (
        Index(
            "ix_incidents_service_severity",
            "service",
            "severity",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    incident_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    service: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        index=True,
        nullable=False,
    )

    incident_date: Mapped[date] = mapped_column(
        Date,
        index=True,
        nullable=False,
    )

    symptoms: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    root_cause: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    solution: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )