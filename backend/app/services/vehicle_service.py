"""Vehicle management service layer."""

import math
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle
from app.schemas.common import PaginationMetadata
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleListResponse,
    VehicleResponse,
    VehicleUpdate,
    feet_to_meters,
    lbs_to_kg,
)


def _check_vehicle_access(vehicle: Vehicle, user: User) -> None:
    """Validate that the requesting user owns or administers the vehicle."""
    is_platform_admin = user.role == UserRole.PLATFORM_ADMIN
    is_owner = vehicle.owner_id == user.id

    # If user is in the same company and is a FLEET_MANAGER or COMPANY_ADMIN
    is_company_manager = (
        vehicle.company_id is not None
        and user.role in (UserRole.FLEET_MANAGER, UserRole.COMPANY_ADMIN)
    )

    if not (is_owner or is_platform_admin or is_company_manager):
        raise AuthorizationError(
            message="You do not have permission to view or manage this vehicle",
            code="VEHICLE_ACCESS_DENIED",
        )


async def create_vehicle(
    db: AsyncSession, owner_id: uuid.UUID, vehicle_in: VehicleCreate
) -> VehicleResponse:
    """Create a new vehicle record for a user, converting imperial units if metric are missing."""
    # Resolve metric values (prefer direct metric; fallback to converted imperial)
    length_m = vehicle_in.length_m if vehicle_in.length_m is not None else feet_to_meters(vehicle_in.length_ft)
    width_m = vehicle_in.width_m if vehicle_in.width_m is not None else feet_to_meters(vehicle_in.width_ft)
    height_m = vehicle_in.height_m if vehicle_in.height_m is not None else feet_to_meters(vehicle_in.height_ft)
    gvwr_kg = vehicle_in.gvwr_kg if vehicle_in.gvwr_kg is not None else lbs_to_kg(vehicle_in.gvwr_lbs)
    operating_weight_kg = (
        vehicle_in.operating_weight_kg
        if vehicle_in.operating_weight_kg is not None
        else lbs_to_kg(vehicle_in.operating_weight_lbs)
    )

    vehicle = Vehicle(
        owner_id=owner_id,
        company_id=vehicle_in.company_id,
        registration_id=vehicle_in.registration_id.strip().upper(),
        manufacturer=vehicle_in.manufacturer.strip() if vehicle_in.manufacturer else None,
        model_name=vehicle_in.model_name.strip() if vehicle_in.model_name else None,
        year=vehicle_in.year,
        vehicle_type=vehicle_in.vehicle_type,
        length_m=length_m,
        width_m=width_m,
        height_m=height_m,
        gvwr_kg=gvwr_kg,
        operating_weight_kg=operating_weight_kg,
        axle_count=vehicle_in.axle_count,
        has_trailer=vehicle_in.has_trailer,
        trailer_type=vehicle_in.trailer_type,
        trailer_length_m=vehicle_in.trailer_length_m,
        is_commercial=vehicle_in.is_commercial,
        is_active=True,
    )
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)

    return VehicleResponse.model_validate(vehicle)


async def get_vehicle(
    db: AsyncSession, vehicle_id: uuid.UUID, user: User
) -> VehicleResponse:
    """Fetch a single vehicle by UUID after verifying user access permissions."""
    stmt = select(Vehicle).where(
        Vehicle.id == vehicle_id,
        Vehicle.deleted_at.is_(None),
    )
    vehicle = (await db.execute(stmt)).scalar_one_or_none()

    if not vehicle:
        raise NotFoundError(
            message=f"Vehicle with id '{vehicle_id}' not found",
            code="VEHICLE_NOT_FOUND",
        )

    _check_vehicle_access(vehicle, user)
    return VehicleResponse.model_validate(vehicle)


async def list_user_vehicles(
    db: AsyncSession,
    user: User,
    page: int = 1,
    page_size: int = 20,
) -> VehicleListResponse:
    """List vehicles owned by or accessible to the requesting user."""
    offset = (page - 1) * page_size

    # Filter by user ownership unless platform administrator
    query = select(Vehicle).where(Vehicle.deleted_at.is_(None))
    count_query = select(func.count(Vehicle.id)).where(Vehicle.deleted_at.is_(None))

    if user.role != UserRole.PLATFORM_ADMIN:
        query = query.where(Vehicle.owner_id == user.id)
        count_query = count_query.where(Vehicle.owner_id == user.id)

    total_count = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(page_size)
    vehicles = (await db.execute(query)).scalars().all()

    return VehicleListResponse(
        success=True,
        total=total_count,
        items=[VehicleResponse.model_validate(v) for v in vehicles],
    )


async def update_vehicle(
    db: AsyncSession,
    vehicle_id: uuid.UUID,
    user: User,
    vehicle_update: VehicleUpdate,
) -> VehicleResponse:
    """Update fields on an existing vehicle with dimensional conversions."""
    stmt = select(Vehicle).where(
        Vehicle.id == vehicle_id,
        Vehicle.deleted_at.is_(None),
    )
    vehicle = (await db.execute(stmt)).scalar_one_or_none()

    if not vehicle:
        raise NotFoundError(
            message=f"Vehicle with id '{vehicle_id}' not found",
            code="VEHICLE_NOT_FOUND",
        )

    _check_vehicle_access(vehicle, user)

    # Update simple scalar fields
    if vehicle_update.registration_id is not None:
        vehicle.registration_id = vehicle_update.registration_id.strip().upper()
    if vehicle_update.manufacturer is not None:
        vehicle.manufacturer = vehicle_update.manufacturer.strip()
    if vehicle_update.model_name is not None:
        vehicle.model_name = vehicle_update.model_name.strip()
    if vehicle_update.year is not None:
        vehicle.year = vehicle_update.year
    if vehicle_update.vehicle_type is not None:
        vehicle.vehicle_type = vehicle_update.vehicle_type
    if vehicle_update.axle_count is not None:
        vehicle.axle_count = vehicle_update.axle_count
    if vehicle_update.has_trailer is not None:
        vehicle.has_trailer = vehicle_update.has_trailer
    if vehicle_update.trailer_type is not None:
        vehicle.trailer_type = vehicle_update.trailer_type
    if vehicle_update.trailer_length_m is not None:
        vehicle.trailer_length_m = vehicle_update.trailer_length_m
    if vehicle_update.is_commercial is not None:
        vehicle.is_commercial = vehicle_update.is_commercial
    if vehicle_update.is_active is not None:
        vehicle.is_active = vehicle_update.is_active
    if vehicle_update.company_id is not None:
        vehicle.company_id = vehicle_update.company_id

    # Handle dimensions (direct metric takes priority, else convert imperial if provided)
    if vehicle_update.length_m is not None:
        vehicle.length_m = vehicle_update.length_m
    elif vehicle_update.length_ft is not None:
        vehicle.length_m = feet_to_meters(vehicle_update.length_ft)

    if vehicle_update.width_m is not None:
        vehicle.width_m = vehicle_update.width_m
    elif vehicle_update.width_ft is not None:
        vehicle.width_m = feet_to_meters(vehicle_update.width_ft)

    if vehicle_update.height_m is not None:
        vehicle.height_m = vehicle_update.height_m
    elif vehicle_update.height_ft is not None:
        vehicle.height_m = feet_to_meters(vehicle_update.height_ft)

    if vehicle_update.gvwr_kg is not None:
        vehicle.gvwr_kg = vehicle_update.gvwr_kg
    elif vehicle_update.gvwr_lbs is not None:
        vehicle.gvwr_kg = lbs_to_kg(vehicle_update.gvwr_lbs)

    if vehicle_update.operating_weight_kg is not None:
        vehicle.operating_weight_kg = vehicle_update.operating_weight_kg
    elif vehicle_update.operating_weight_lbs is not None:
        vehicle.operating_weight_kg = lbs_to_kg(vehicle_update.operating_weight_lbs)

    await db.commit()
    await db.refresh(vehicle)

    return VehicleResponse.model_validate(vehicle)


async def delete_vehicle(
    db: AsyncSession, vehicle_id: uuid.UUID, user: User
) -> None:
    """Soft delete a vehicle record by setting deleted_at."""
    stmt = select(Vehicle).where(
        Vehicle.id == vehicle_id,
        Vehicle.deleted_at.is_(None),
    )
    vehicle = (await db.execute(stmt)).scalar_one_or_none()

    if not vehicle:
        raise NotFoundError(
            message=f"Vehicle with id '{vehicle_id}' not found",
            code="VEHICLE_NOT_FOUND",
        )

    _check_vehicle_access(vehicle, user)

    vehicle.deleted_at = datetime.now(timezone.utc)
    vehicle.is_active = False
    await db.commit()
