"""Vehicle CRUD API endpoints."""

import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleListResponse,
    VehicleResponse,
    VehicleUpdate,
)
from app.services import vehicle_service

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new vehicle",
    description="Add a commercial truck, delivery van, or trailer to user fleet.",
)
async def create_vehicle(
    vehicle_in: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VehicleResponse:
    """Create a new vehicle record."""
    return await vehicle_service.create_vehicle(
        db=db, owner_id=current_user.id, vehicle_in=vehicle_in
    )


@router.get(
    "",
    response_model=VehicleListResponse,
    status_code=status.HTTP_200_OK,
    summary="List vehicles",
    description="Retrieve all vehicles owned by or accessible to current user.",
)
async def list_vehicles(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VehicleListResponse:
    """List accessible vehicles with pagination."""
    return await vehicle_service.list_user_vehicles(
        db=db, user=current_user, page=page, page_size=page_size
    )


@router.get(
    "/{id}",
    response_model=VehicleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get vehicle by ID",
    description="Retrieve specific vehicle dimensions and registration information.",
)
async def get_vehicle(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VehicleResponse:
    """Get single vehicle details."""
    return await vehicle_service.get_vehicle(
        db=db, vehicle_id=id, user=current_user
    )


@router.put(
    "/{id}",
    response_model=VehicleResponse,
    status_code=status.HTTP_200_OK,
    summary="Update vehicle details",
    description="Modify vehicle dimensions, commercial registration, or trailer details.",
)
async def update_vehicle(
    id: uuid.UUID,
    vehicle_update: VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VehicleResponse:
    """Update existing vehicle."""
    return await vehicle_service.update_vehicle(
        db=db, vehicle_id=id, user=current_user, vehicle_update=vehicle_update
    )


@router.delete(
    "/{id}",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete vehicle",
    description="Soft delete a vehicle from the fleet.",
)
async def delete_vehicle(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[None]:
    """Delete a vehicle by ID."""
    await vehicle_service.delete_vehicle(
        db=db, vehicle_id=id, user=current_user
    )
    return SuccessResponse(message="Vehicle successfully deleted")
