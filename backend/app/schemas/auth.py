"""Authentication and user management request/response schemas."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserRegister(BaseModel):
    """Payload for creating a new user account."""
    email: EmailStr = Field(description="User primary email address")
    password: str = Field(min_length=8, max_length=128, description="Plaintext password (min 8 characters)")
    first_name: str = Field(min_length=1, max_length=100, description="User first name")
    last_name: str = Field(min_length=1, max_length=100, description="User last name")
    phone: Optional[str] = Field(default=None, max_length=30, description="Optional phone number")
    role: UserRole = Field(default=UserRole.DRIVER, description="Initial system role")


class UserLogin(BaseModel):
    """Payload for user authentication."""
    email: EmailStr = Field(description="Registered account email")
    password: str = Field(description="Account password")
    device_info: Optional[str] = Field(default=None, max_length=255, description="Client device description")


class UserResponse(BaseModel):
    """Public user profile information."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Response returned upon successful authentication or token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token lifespan in seconds")
    user: UserResponse


class TokenRefresh(BaseModel):
    """Payload to exchange a refresh token for a new access token."""
    refresh_token: str = Field(description="Valid JWT refresh token")


class UserUpdate(BaseModel):
    """Payload for modifying an existing user's profile details."""
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=30)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)
