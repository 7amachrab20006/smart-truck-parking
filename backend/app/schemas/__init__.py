"""Schemas package initialization."""

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    UserUpdate,
    TokenResponse,
    TokenRefresh,
)
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse,
    VehicleListResponse,
    meters_to_feet,
    feet_to_meters,
    kg_to_lbs,
    lbs_to_kg,
)
from app.schemas.common import (
    PaginatedResponse,
    PaginationMetadata,
    SuccessResponse,
    ErrorResponse,
    HealthResponse,
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "TokenResponse",
    "TokenRefresh",
    "VehicleCreate",
    "VehicleUpdate",
    "VehicleResponse",
    "VehicleListResponse",
    "meters_to_feet",
    "feet_to_meters",
    "kg_to_lbs",
    "lbs_to_kg",
    "PaginatedResponse",
    "PaginationMetadata",
    "SuccessResponse",
    "ErrorResponse",
    "HealthResponse",
]
