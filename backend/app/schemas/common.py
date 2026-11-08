"""Common generic schemas for API responses, pagination, and health status."""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Structured error payload details."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standardized error envelope."""
    success: bool = False
    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[T]):
    """Standardized success envelope for single item responses."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None


class PaginationMetadata(BaseModel):
    """Metadata regarding pagination state."""
    page: int = Field(ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(ge=1, description="Number of items per page")
    total_items: int = Field(ge=0, description="Total number of items across all pages")
    total_pages: int = Field(ge=0, description="Total number of pages available")
    has_next: bool = Field(description="True if another page exists after current")
    has_previous: bool = Field(description="True if a previous page exists before current")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated list response envelope."""
    success: bool = True
    items: List[T]
    pagination: PaginationMetadata


class HealthResponse(BaseModel):
    """Application and subsystem health status."""
    status: str = "healthy"
    version: str
    environment: str
    database_connected: bool
    timestamp: str
