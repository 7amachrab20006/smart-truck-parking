"""Vehicle schemas and dimensional unit conversion utilities."""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models.vehicle import VehicleType

# Conversion constants
METERS_TO_FEET = 3.28084
FEET_TO_METERS = 0.3048
KG_TO_LBS = 2.20462
LBS_TO_KG = 0.45359237


def feet_to_meters(feet: Optional[float]) -> Optional[float]:
    """Convert feet to meters rounded to 2 decimal places."""
    if feet is None:
        return None
    return round(feet * FEET_TO_METERS, 2)


def meters_to_feet(meters: Optional[float]) -> Optional[float]:
    """Convert meters to feet rounded to 2 decimal places."""
    if meters is None:
        return None
    return round(meters * METERS_TO_FEET, 2)


def lbs_to_kg(lbs: Optional[float]) -> Optional[float]:
    """Convert pounds (lbs) to kilograms (kg) rounded to 2 decimal places."""
    if lbs is None:
        return None
    return round(lbs * LBS_TO_KG, 2)


def kg_to_lbs(kg: Optional[float]) -> Optional[float]:
    """Convert kilograms (kg) to pounds (lbs) rounded to 2 decimal places."""
    if kg is None:
        return None
    return round(kg * KG_TO_LBS, 2)


class VehicleBase(BaseModel):
    """Shared base fields for vehicle payloads."""
    registration_id: str = Field(min_length=1, max_length=50, description="License plate or DOT registration")
    manufacturer: Optional[str] = Field(default=None, max_length=100)
    model_name: Optional[str] = Field(default=None, max_length=100)
    year: Optional[int] = Field(default=None, ge=1900, le=2100)
    vehicle_type: VehicleType = Field(default=VehicleType.DELIVERY_VAN)
    length_m: Optional[float] = Field(default=None, ge=0.0, description="Length in meters")
    width_m: Optional[float] = Field(default=None, ge=0.0, description="Width in meters")
    height_m: Optional[float] = Field(default=None, ge=0.0, description="Height in meters")
    gvwr_kg: Optional[float] = Field(default=None, ge=0.0, description="Gross Vehicle Weight Rating in kg")
    operating_weight_kg: Optional[float] = Field(default=None, ge=0.0, description="Operating weight in kg")
    axle_count: Optional[int] = Field(default=2, ge=2, le=20)
    has_trailer: bool = Field(default=False)
    trailer_type: Optional[str] = Field(default=None, max_length=100)
    trailer_length_m: Optional[float] = Field(default=None, ge=0.0)
    is_commercial: bool = Field(default=True)
    company_id: Optional[uuid.UUID] = Field(default=None, description="Optional fleet company UUID")


class VehicleCreate(VehicleBase):
    """Payload to register a new vehicle."""
    # Optional imperial fields that automatically convert if metric fields are omitted
    length_ft: Optional[float] = Field(default=None, ge=0.0)
    width_ft: Optional[float] = Field(default=None, ge=0.0)
    height_ft: Optional[float] = Field(default=None, ge=0.0)
    gvwr_lbs: Optional[float] = Field(default=None, ge=0.0)
    operating_weight_lbs: Optional[float] = Field(default=None, ge=0.0)


class VehicleUpdate(BaseModel):
    """Payload for partial vehicle updates."""
    registration_id: Optional[str] = Field(default=None, max_length=50)
    manufacturer: Optional[str] = Field(default=None, max_length=100)
    model_name: Optional[str] = Field(default=None, max_length=100)
    year: Optional[int] = Field(default=None, ge=1900, le=2100)
    vehicle_type: Optional[VehicleType] = None
    length_m: Optional[float] = Field(default=None, ge=0.0)
    width_m: Optional[float] = Field(default=None, ge=0.0)
    height_m: Optional[float] = Field(default=None, ge=0.0)
    gvwr_kg: Optional[float] = Field(default=None, ge=0.0)
    operating_weight_kg: Optional[float] = Field(default=None, ge=0.0)
    axle_count: Optional[int] = Field(default=None, ge=2, le=20)
    has_trailer: Optional[bool] = None
    trailer_type: Optional[str] = Field(default=None, max_length=100)
    trailer_length_m: Optional[float] = Field(default=None, ge=0.0)
    is_commercial: Optional[bool] = None
    is_active: Optional[bool] = None
    company_id: Optional[uuid.UUID] = None

    # Imperial inputs for convenience
    length_ft: Optional[float] = Field(default=None, ge=0.0)
    width_ft: Optional[float] = Field(default=None, ge=0.0)
    height_ft: Optional[float] = Field(default=None, ge=0.0)
    gvwr_lbs: Optional[float] = Field(default=None, ge=0.0)
    operating_weight_lbs: Optional[float] = Field(default=None, ge=0.0)


class VehicleResponse(BaseModel):
    """Vehicle response presentation schema including both metric and imperial measurements."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    company_id: Optional[uuid.UUID] = None
    registration_id: str
    manufacturer: Optional[str] = None
    model_name: Optional[str] = None
    year: Optional[int] = None
    vehicle_type: VehicleType
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    height_m: Optional[float] = None
    gvwr_kg: Optional[float] = None
    operating_weight_kg: Optional[float] = None
    axle_count: Optional[int] = None
    has_trailer: bool
    trailer_type: Optional[str] = None
    trailer_length_m: Optional[float] = None
    is_commercial: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def length_ft(self) -> Optional[float]:
        """Length converted to feet."""
        return meters_to_feet(self.length_m)

    @computed_field
    @property
    def width_ft(self) -> Optional[float]:
        """Width converted to feet."""
        return meters_to_feet(self.width_m)

    @computed_field
    @property
    def height_ft(self) -> Optional[float]:
        """Height converted to feet."""
        return meters_to_feet(self.height_m)

    @computed_field
    @property
    def gvwr_lbs(self) -> Optional[float]:
        """GVWR converted to pounds."""
        return kg_to_lbs(self.gvwr_kg)

    @computed_field
    @property
    def operating_weight_lbs(self) -> Optional[float]:
        """Operating weight converted to pounds."""
        return kg_to_lbs(self.operating_weight_kg)


class VehicleListResponse(BaseModel):
    """Response containing a list of vehicles."""
    success: bool = True
    total: int
    items: List[VehicleResponse]
