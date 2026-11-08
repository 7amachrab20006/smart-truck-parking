"""Security module: password hashing, JWT generation and verification, and role dependencies."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.database.session import get_db
from app.models.user import User, UserRole

# Crypt context using Argon2 password hasher
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scheme for Swagger UI & token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its Argon2 hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    role: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT refresh token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    """Decode and validate a JWT token payload."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_type = payload.get("type")
        if token_type != expected_type:
            raise AuthenticationError(
                message=f"Invalid token type: expected {expected_type}, got {token_type}",
                code="INVALID_TOKEN_TYPE",
            )
        sub = payload.get("sub")
        if not sub:
            raise AuthenticationError(
                message="Token payload is missing subject claim",
                code="INVALID_TOKEN",
            )
        return payload
    except JWTError as exc:
        raise AuthenticationError(
            message=f"Token validation failed: {str(exc)}",
            code="INVALID_TOKEN",
        ) from exc


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency to extract and authenticate current user from Bearer token."""
    if not token:
        raise AuthenticationError(
            message="Missing authentication credentials",
            code="NOT_AUTHENTICATED",
        )

    payload = verify_token(token, expected_type="access")
    user_id_str = payload.get("sub")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except (ValueError, TypeError) as exc:
        raise AuthenticationError(
            message="Invalid user identifier in token",
            code="INVALID_USER_ID",
        ) from exc

    stmt = select(User).where(
        User.id == user_uuid,
        User.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError(
            message="User account associated with token was not found",
            code="USER_NOT_FOUND",
        )

    if not user.is_active:
        raise AuthenticationError(
            message="User account is inactive or disabled",
            code="USER_INACTIVE",
        )

    return user


def require_role(*allowed_roles: UserRole) -> Callable:
    """Dependency factory restricting route access to specified UserRoles."""

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role = current_user.role
        # Accept enum or string representation
        if isinstance(user_role, str):
            try:
                user_role = UserRole(user_role)
            except ValueError:
                pass

        if user_role not in allowed_roles:
            role_names = [r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles]
            raise AuthorizationError(
                message=f"Access denied. Requires one of roles: {', '.join(role_names)}",
                code="INSUFFICIENT_PERMISSIONS",
                details={"user_role": str(current_user.role), "required_roles": role_names},
            )
        return current_user

    return role_checker
