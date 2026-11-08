"""Community reporting models for crowdsourced signage and curb condition issues."""

import enum
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class ReportCategory(str, enum.Enum):
    """Categorization of community reported curb events."""
    SIGN_MISSING = "SIGN_MISSING"
    SIGN_DAMAGED = "SIGN_DAMAGED"
    SIGN_CONFLICT = "SIGN_CONFLICT"
    CONSTRUCTION_BLOCK = "CONSTRUCTION_BLOCK"
    ILLEGAL_PARKING = "ILLEGAL_PARKING"
    CURB_CHANGE = "CURB_CHANGE"
    OTHER = "OTHER"


class ReportStatus(str, enum.Enum):
    """Review and verification status for crowd-sourced reports."""
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class CommunityReport(Base, TimestampMixin):
    """User submitted report verifying or disputing signs and curb conditions."""

    __tablename__ = "community_reports"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[ReportCategory] = mapped_column(
        String(50),
        default=ReportCategory.SIGN_CONFLICT,
        nullable=False,
    )
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    photo_urls: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        String(50),
        default=ReportStatus.PENDING,
        nullable=False,
    )
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    reviewer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reviewed_by])
