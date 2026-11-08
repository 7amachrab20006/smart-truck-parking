"""Regulatory Engine REST API Endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.common import SuccessResponse
from app.schemas.regulation import (
    RegulationEvaluateRequest,
    RegulationEvaluateResponse,
)
from app.services.regulation_service import RegulationService

router = APIRouter(prefix="/regulations", tags=["Regulations"])


@router.post(
    "/evaluate",
    response_model=SuccessResponse[RegulationEvaluateResponse],
    summary="Evaluate regulatory legality for a vehicle, position, and activity",
)
async def evaluate_regulation(
    request: RegulationEvaluateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Answers the core business question:
    'Can this specific vehicle perform this activity at this location at this date and time?'
    """
    service = RegulationService(db)
    result = await service.evaluate_regulation(request)
    return SuccessResponse(data=result, message="Regulatory evaluation completed.")
