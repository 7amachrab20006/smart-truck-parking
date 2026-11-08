"""Model package imports for Alembic discovery and unified entity access."""

from app.database.base import Base, TimestampMixin
from app.models.user import User, UserRole, RefreshToken
from app.models.company import Company, CompanyMember
from app.models.vehicle import Vehicle, VehicleType, VehiclePermit
from app.models.regulation import (
    Jurisdiction,
    ParkingRegulation,
    RegulationType,
    VerificationStatus,
    RuleTargetType,
    RegulationTimeRule,
    RegulationVehicleRule,
    RegulationException,
)
from app.models.street import StreetSegment, CurbSegment, CurbSide
from app.models.data_source import DataSource, DataImportJob, ImportJobStatus
from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.parking_session import ParkingSession, ParkingSessionStatus
from app.models.report import CommunityReport, ReportCategory, ReportStatus
from app.models.fleet import FleetAssignment, Subscription
from app.models.audit import AuditLog

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "UserRole",
    "RefreshToken",
    "Company",
    "CompanyMember",
    "Vehicle",
    "VehicleType",
    "VehiclePermit",
    "Jurisdiction",
    "ParkingRegulation",
    "RegulationType",
    "VerificationStatus",
    "RuleTargetType",
    "RegulationTimeRule",
    "RegulationVehicleRule",
    "RegulationException",
    "StreetSegment",
    "CurbSegment",
    "CurbSide",
    "DataSource",
    "DataImportJob",
    "ImportJobStatus",
    "Alert",
    "AlertSeverity",
    "AlertType",
    "ParkingSession",
    "ParkingSessionStatus",
    "CommunityReport",
    "ReportCategory",
    "ReportStatus",
    "FleetAssignment",
    "Subscription",
    "AuditLog",
]
