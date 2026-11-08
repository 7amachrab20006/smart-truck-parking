"""Data source and data import job models for ingestion pipelines."""

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ImportJobStatus(str, enum.Enum):
    """Execution status of an automated data ingest job."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class DataSource(Base):
    """External open data portal or private feed configuration (e.g., NYC DOT Open Data)."""

    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    organization: Mapped[str] = mapped_column(String(150), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    data_format: Mapped[str] = mapped_column(String(50), default="JSON", nullable=False)
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    attribution_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    update_frequency: Mapped[str] = mapped_column(String(50), default="DAILY", nullable=False)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_successful_sync: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    import_jobs: Mapped[List["DataImportJob"]] = relationship(
        "DataImportJob", back_populates="data_source", cascade="all, delete-orphan"
    )
    regulations: Mapped[List["ParkingRegulation"]] = relationship(
        "ParkingRegulation", back_populates="data_source"
    )


class DataImportJob(Base):
    """Audit record of data ingestion runs tracking record throughput and errors."""

    __tablename__ = "data_import_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    data_source_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("data_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ImportJobStatus] = mapped_column(
        String(50),
        default=ImportJobStatus.PENDING,
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    records_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_imported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_log: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    source_checksum: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    data_source: Mapped["DataSource"] = relationship("DataSource", back_populates="import_jobs")
