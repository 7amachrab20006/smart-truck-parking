"""Health and readiness check endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.session import get_db
from app.schemas.common import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application health check",
    description="Check application liveness and metadata.",
)
async def health_check() -> HealthResponse:
    """Basic service health check."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        database_connected=False,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/db",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Database health check",
    description="Test database connectivity by executing a SELECT 1 ping.",
)
async def db_health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Database connectivity and readiness check."""
    db_connected = False
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            db_connected = True
    except Exception:
        db_connected = False

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        database_connected=db_connected,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
