"""Vehicle and permit database models."""

import enum
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class VehicleType(str, enum.Enum):
    """Classification of commercial and freight vehicles."""
    DELIVERY_VAN = "DELIVERY_VAN"
    BOX_TRUCK = "BOX_TRUCK"
    STRAIGHT_TRUCK = "STRAIGHT_TRUCK"
    HEAVY_DUTY_TRUCK = "HEAVY_DUTY_TRUCK"
    SEMI_TRUCK = "SEMI_TRUCK"


class Vehicle(Base, TimestampMixin):
    """Vehicle profile storing dimensional and weight attributes for regulation compliance."""

    __tablename__ = "vehicles"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    registration_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vehicle_type: Mapped[VehicleType] = mapped_column(
        String(50),
        default=VehicleType.DELIVERY_VAN,
        nullable=False,
    )
    length_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    width_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    height_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gvwr_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    operating_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    axle_count: Mapped[Optional[int]] = mapped_column(Integer, default=2, nullable=True)
    has_trailer: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trailer_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    trailer_length_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_commercial: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship(
        "User", back_populates="vehicles", foreign_keys=[owner_id]
    )
    company: Mapped[Optional["Company"]] = relationship(
        "Company", back_populates="vehicles", foreign_keys=[company_id]
    )
    permits: Mapped[List["VehiclePermit"]] = relationship(
        "VehiclePermit", back_populates="vehicle", cascade="all, delete-orphan"
    )
    parking_sessions: Mapped[List["ParkingSession"]] = relationship(
        "ParkingSession", back_populates="vehicle"
    )
    fleet_assignments: Mapped[List["FleetAssignment"]] = relationship(
        "FleetAssignment", back_populates="vehicle"
    )


class VehiclePermit(Base):
    """Permits associated with a specific vehicle (e.g., DOT commercial permits, oversized)."""

    __tablename__ = "vehicle_permits"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permit_type: Mapped[str] = mapped_column(String(100), nullable=False)
    permit_number: Mapped[str] = mapped_column(String(100), nullable=False)
    issuing_authority: Mapped[str] = mapped_column(String(150), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="permits")
