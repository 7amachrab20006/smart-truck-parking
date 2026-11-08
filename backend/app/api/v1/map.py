"""Smart Map and Spatial Layer Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.common import SuccessResponse
from app.schemas.regulation import (
    MapLoadingZoneItem,
    MapRegulationItem,
    MapTruckRouteItem,
)
from app.services.regulation_service import RegulationService

router = APIRouter(prefix="/map", tags=["Smart Map"])


@router.get(
    "/regulations",
    response_model=SuccessResponse[List[MapRegulationItem]],
    summary="Get parking and stopping regulations for map visualization",
)
async def get_map_regulations(
    latitude: float = Query(default=40.7580, ge=-90.0, le=90.0),
    longitude: float = Query(default=-73.9855, ge=-180.0, le=180.0),
    radius_meters: float = Query(default=1000.0, ge=100.0, le=10000.0),
    db: AsyncSession = Depends(get_db),
):
    """Returns spatial regulation overlays with standard status colors (RED, GREEN, ORANGE, BLUE, GRAY)."""
    service = RegulationService(db)
    items = await service.get_map_regulations(latitude, longitude, radius_meters)
    return SuccessResponse(data=items, message=f"Retrieved {len(items)} regulation overlays.")


@router.get(
    "/loading-zones",
    response_model=SuccessResponse[List[MapLoadingZoneItem]],
    summary="Get verified commercial and truck loading zones",
)
async def get_loading_zones(
    borough: str = Query(default="MANHATTAN"),
    db: AsyncSession = Depends(get_db),
):
    """Returns officially designated commercial and neighborhood loading zones."""
    service = RegulationService(db)
    items = await service.get_map_loading_zones(borough)
    return SuccessResponse(data=items, message=f"Retrieved {len(items)} loading zones.")


@router.get(
    "/truck-routes",
    response_model=SuccessResponse[List[MapTruckRouteItem]],
    summary="Get designated NYC truck route network",
)
async def get_truck_routes(
    borough: str = Query(default="MANHATTAN"),
    db: AsyncSession = Depends(get_db),
):
    """Returns designated through and local truck routes."""
    service = RegulationService(db)
    items = await service.get_map_truck_routes(borough)
    return SuccessResponse(data=items, message=f"Retrieved {len(items)} truck routes.")
