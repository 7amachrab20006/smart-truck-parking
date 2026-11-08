"""Real-time parking and route compliance alert models."""

import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AlertSeverity(str, enum.Enum):
    """Alert urgency levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertType(str, enum.Enum):
    """Categories of driver notifications."""
    PARKING_EXPIRY = "PARKING_EXPIRY"
    RESTRICTION_CHANGE = "RESTRICTION_CHANGE"
    STREET_SWEEPING = "STREET_SWEEPING"
    OVERSIZED_WARNING = "OVERSIZED_WARNING"
    TOW_ZONE_WARNING = "TOW_ZONE_WARNING"
    SYSTEM_NOTIFICATION = "SYSTEM_NOTIFICATION"


class Alert(Base):
    """Notification emitted to driver or fleet manager regarding parking rules or vehicle violations."""

    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vehicle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    alert_type: Mapped[str] = mapped_column(String(50), default=AlertType.SYSTEM_NOTIFICATION, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(String(20), default=AlertSeverity.INFO, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    regulation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("parking_regulations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    restriction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle")
    regulation: Mapped[Optional["ParkingRegulation"]] = relationship("ParkingRegulation")
