"""Street network and curb segment database models."""

import enum
import uuid
from typing import List, Optional
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class CurbSide(str, enum.Enum):
    """Curb side of street in direction of digitization."""
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BOTH = "BOTH"
    UNKNOWN = "UNKNOWN"


class StreetSegment(Base, TimestampMixin):
    """Street centerline segment with truck routing and physical attributes."""

    __tablename__ = "street_segments"

    jurisdiction_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("jurisdictions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    street_name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    from_street: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    to_street: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    borough: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    road_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_truck_route: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    truck_route_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # THROUGH / LOCAL
    speed_limit_mph: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lanes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    one_way: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    direction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # FT, TF, TWO_WAY
    geometry: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Placeholder for PostGIS LineString

    # Relationships
    jurisdiction: Mapped[Optional["Jurisdiction"]] = relationship("Jurisdiction", back_populates="street_segments")
    curb_segments: Mapped[List["CurbSegment"]] = relationship(
        "CurbSegment", back_populates="street_segment", cascade="all, delete-orphan"
    )
    regulations: Mapped[List["ParkingRegulation"]] = relationship(
        "ParkingRegulation", back_populates="street_segment"
    )


class CurbSegment(Base, TimestampMixin):
    """Curb zone representing designated physical roadside space for parking/loading."""

    __tablename__ = "curb_segments"

    street_segment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("street_segments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    side: Mapped[CurbSide] = mapped_column(
        String(20),
        default=CurbSide.RIGHT,
        nullable=False,
    )
    from_distance_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    to_distance_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    curb_length_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geometry: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Placeholder for PostGIS LineString

    # Relationships
    street_segment: Mapped["StreetSegment"] = relationship("StreetSegment", back_populates="curb_segments")
    regulations: Mapped[List["ParkingRegulation"]] = relationship(
        "ParkingRegulation", back_populates="curb_segment"
    )
