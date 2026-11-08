"""Authentication and user account service layer."""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.user import RefreshToken, User
from app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)


def _hash_token(token: str) -> str:
    """Generate SHA-256 hash of a token string for safe database lookup."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def register_user(db: AsyncSession, user_in: UserRegister) -> UserResponse:
    """Register a new user account if the email is not already taken."""
    stmt = select(User).where(User.email == user_in.email.lower().strip())
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise ConflictError(
            message=f"An account with email '{user_in.email}' already exists",
            code="EMAIL_ALREADY_EXISTS",
        )

    hashed_pw = hash_password(user_in.password)
    user = User(
        email=user_in.email.lower().strip(),
        password_hash=hashed_pw,
        first_name=user_in.first_name.strip(),
        last_name=user_in.last_name.strip(),
        phone=user_in.phone.strip() if user_in.phone else None,
        role=user_in.role,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


async def authenticate_user(
    db: AsyncSession, login_data: UserLogin
) -> TokenResponse:
    """Authenticate user credentials and issue an access/refresh token pair."""
    stmt = select(User).where(
        User.email == login_data.email.lower().strip(),
        User.deleted_at.is_(None),
    )
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise AuthenticationError(
            message="Invalid email or password",
            code="INVALID_CREDENTIALS",
        )

    if not user.is_active:
        raise AuthenticationError(
            message="Your account has been deactivated. Please contact support.",
            code="ACCOUNT_INACTIVE",
        )

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)

    # Issue JWT tokens
    access_token = create_access_token(
        subject=str(user.id),
        role=str(user.role.value if hasattr(user.role, "value") else user.role),
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    # Store refresh token record
    token_hash = _hash_token(refresh_token)
    decoded_refresh = verify_token(refresh_token, expected_type="refresh")
    exp_timestamp = decoded_refresh.get("exp")
    expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        device_info=login_data.device_info,
        expires_at=expires_at,
        is_revoked=False,
    )
    db.add(db_refresh_token)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


async def refresh_access_token(
    db: AsyncSession, refresh_token_str: str
) -> TokenResponse:
    """Validate a refresh token and issue a fresh access and refresh token pair."""
    payload = verify_token(refresh_token_str, expected_type="refresh")
    user_id_str = payload.get("sub")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except (ValueError, TypeError) as exc:
        raise AuthenticationError(message="Invalid token subject", code="INVALID_TOKEN") from exc

    token_hash = _hash_token(refresh_token_str)
    stmt = select(RefreshToken).where(
        RefreshToken.token_hash == token_hash,
        RefreshToken.user_id == user_uuid,
    )
    db_token = (await db.execute(stmt)).scalar_one_or_none()

    if not db_token or db_token.is_revoked:
        raise AuthenticationError(
            message="Refresh token is revoked or unrecognized",
            code="TOKEN_REVOKED",
        )

    now = datetime.now(timezone.utc)
    # Check expiration (ensure tz-aware comparison)
    exp = db_token.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp < now:
        db_token.is_revoked = True
        await db.commit()
        raise AuthenticationError(
            message="Refresh token has expired",
            code="TOKEN_EXPIRED",
        )

    # Fetch user
    user_stmt = select(User).where(User.id == user_uuid, User.deleted_at.is_(None))
    user = (await db.execute(user_stmt)).scalar_one_or_none()

    if not user or not user.is_active:
        raise AuthenticationError(
            message="User account is inactive or not found",
            code="USER_INACTIVE",
        )

    # Invalidate previous refresh token (rotation)
    db_token.is_revoked = True

    # Issue new pair
    new_access_token = create_access_token(
        subject=str(user.id),
        role=str(user.role.value if hasattr(user.role, "value") else user.role),
    )
    new_refresh_token = create_refresh_token(subject=str(user.id))

    new_decoded = verify_token(new_refresh_token, expected_type="refresh")
    new_expires_at = datetime.fromtimestamp(new_decoded.get("exp"), tz=timezone.utc)

    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=_hash_token(new_refresh_token),
        device_info=db_token.device_info,
        expires_at=new_expires_at,
        is_revoked=False,
    )
    db.add(new_db_token)
    await db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


async def logout_user(db: AsyncSession, refresh_token_str: str) -> None:
    """Revoke a refresh token to terminate session."""
    token_hash = _hash_token(refresh_token_str)
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .values(is_revoked=True)
    )
    await db.execute(stmt)
    await db.commit()


def get_user_profile(user: User) -> UserResponse:
    """Format and return current user profile response."""
    return UserResponse.model_validate(user)


async def update_user_profile(
    db: AsyncSession, user: User, user_update: UserUpdate
) -> UserResponse:
    """Update current user profile information."""
    if user_update.first_name is not None:
        user.first_name = user_update.first_name.strip()
    if user_update.last_name is not None:
        user.last_name = user_update.last_name.strip()
    if user_update.phone is not None:
        user.phone = user_update.phone.strip()
    if user_update.password is not None:
        user.password_hash = hash_password(user_update.password)

    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)
