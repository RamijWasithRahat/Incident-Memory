from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
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


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    incident_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "incidents.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    service: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    __table_args__ = (
        Index(
            "ix_document_chunks_service_section",
            "service",
            "section",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    section: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        nullable=False,
    )

    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    service: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    severity: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    incident_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(384),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )