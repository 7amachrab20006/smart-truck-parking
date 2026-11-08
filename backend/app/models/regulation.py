"""Parking regulation models including temporal and vehicle-specific rules."""

import enum
import uuid
from datetime import date, datetime, time
from typing import Any, List, Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Time,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class RegulationType(str, enum.Enum):
    """Types of curb regulations."""
    NO_PARKING = "NO_PARKING"
    NO_STANDING = "NO_STANDING"
    NO_STOPPING = "NO_STOPPING"
    LOADING_ONLY = "LOADING_ONLY"
    TRUCK_LOADING_ONLY = "TRUCK_LOADING_ONLY"
    COMMERCIAL_LOADING = "COMMERCIAL_LOADING"
    METERED_PARKING = "METERED_PARKING"
    TEMPORARY_RESTRICTION = "TEMPORARY_RESTRICTION"


class VerificationStatus(str, enum.Enum):
    """Regulation source data verification status."""
    IMPORTED = "IMPORTED"
    VERIFIED = "VERIFIED"
    DISPUTED = "DISPUTED"
    UNVERIFIED = "UNVERIFIED"


class RuleTargetType(str, enum.Enum):
    """Application rule action (include or exclude targeted vehicles)."""
    INCLUDE = "INCLUDE"
    EXCLUDE = "EXCLUDE"


class Jurisdiction(Base):
    """Municipal or regulatory jurisdiction entity governing parking rules."""

    __tablename__ = "jurisdictions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    borough: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="America/New_York", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    regulations: Mapped[List["ParkingRegulation"]] = relationship(
        "ParkingRegulation", back_populates="jurisdiction"
    )
    street_segments: Mapped[List["StreetSegment"]] = relationship(
        "StreetSegment", back_populates="jurisdiction"
    )


class ParkingRegulation(Base, TimestampMixin):
    """Core curb parking regulation entity."""

    __tablename__ = "parking_regulations"

    curb_segment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("curb_segments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    street_segment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("street_segments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    jurisdiction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("jurisdictions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    data_source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("data_sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_record_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    regulation_type: Mapped[RegulationType] = mapped_column(
        String(50),
        default=RegulationType.NO_PARKING,
        nullable=False,
    )
    street_name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    street_side: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    from_cross_street: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    to_cross_street: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    sign_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effective_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_temporary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        String(50),
        default=VerificationStatus.IMPORTED,
        nullable=False,
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, default=1.0, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    geometry: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Placeholder for PostGIS Geometry
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    jurisdiction: Mapped["Jurisdiction"] = relationship("Jurisdiction", back_populates="regulations")
    curb_segment: Mapped[Optional["CurbSegment"]] = relationship("CurbSegment", back_populates="regulations")
    street_segment: Mapped[Optional["StreetSegment"]] = relationship("StreetSegment", back_populates="regulations")
    data_source: Mapped[Optional["DataSource"]] = relationship("DataSource", back_populates="regulations")
    time_rules: Mapped[List["RegulationTimeRule"]] = relationship(
        "RegulationTimeRule", back_populates="regulation", cascade="all, delete-orphan"
    )
    vehicle_rules: Mapped[List["RegulationVehicleRule"]] = relationship(
        "RegulationVehicleRule", back_populates="regulation", cascade="all, delete-orphan"
    )
    exceptions: Mapped[List["RegulationException"]] = relationship(
        "RegulationException", back_populates="regulation", cascade="all, delete-orphan"
    )


class RegulationTimeRule(Base):
    """Temporal schedule when a regulation applies (days, start/end hours, max duration)."""

    __tablename__ = "regulation_time_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    regulation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("parking_regulations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    days_of_week: Mapped[List[int]] = mapped_column(JSON, default=list, nullable=False)  # [0-6] Mon-Sun
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    max_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_overnight: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    regulation: Mapped["ParkingRegulation"] = relationship("ParkingRegulation", back_populates="time_rules")


class RegulationVehicleRule(Base):
    """Vehicle-specific constraints, dimensional limits, or exemptions for a regulation."""

    __tablename__ = "regulation_vehicle_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    regulation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("parking_regulations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    applies_to: Mapped[RuleTargetType] = mapped_column(
        String(20),
        default=RuleTargetType.INCLUDE,
        nullable=False,
    )
    vehicle_types: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    max_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_height_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_length_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_width_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_commercial_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_permit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    regulation: Mapped["ParkingRegulation"] = relationship("ParkingRegulation", back_populates="vehicle_rules")


class RegulationException(Base):
    """Holidays, emergency suspensions, or specific exceptions modifying regulations."""

    __tablename__ = "regulation_exceptions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    regulation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("parking_regulations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exception_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    suspends_regulation: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    regulation: Mapped["ParkingRegulation"] = relationship("ParkingRegulation", back_populates="exceptions")
