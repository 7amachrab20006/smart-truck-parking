"""Pydantic schemas for regulatory evaluation and map queries."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.domain.regulatory_engine.models import (
    AlternativeLocation,
    EvaluationDecision,
    RequestedActivity,
    StreetSide,
)


class RegulationEvaluateRequest(BaseModel):
    """Input payload for regulatory engine evaluation."""
    vehicle_id: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0, description="WGS84 latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="WGS84 longitude")
    heading: Optional[float] = Field(None, ge=0.0, le=360.0, description="Compass heading in degrees")
    activity: RequestedActivity = Field(default=RequestedActivity.PARK, description="Target activity")
    eval_time: Optional[datetime] = Field(None, description="Timestamp to evaluate (defaults to now)")
    street_name: Optional[str] = None
    street_side: Optional[StreetSide] = Field(default=StreetSide.UNKNOWN)
    # Manual vehicle specs if vehicle_id is not saved yet
    vehicle_type: Optional[str] = "DELIVERY_VAN"
    height_m: Optional[float] = None
    width_m: Optional[float] = None
    length_m: Optional[float] = None
    weight_kg: Optional[float] = None
    is_commercial: bool = True
    axle_count: Optional[int] = 2


class RegulationResponse(BaseModel):
    """Normalized regulation details."""
    id: str
    classification: str
    street_name: str
    street_side: str
    sign_text: Optional[str] = None
    source: str
    confidence_score: float
    verification_status: str
    is_commercial_only: bool = False


class RegulationEvaluateResponse(BaseModel):
    """Output payload from regulatory engine evaluation."""
    decision: EvaluationDecision
    explanation: str
    status_color: str  # RED, GREEN, ORANGE, BLUE, GRAY
    applicable_regulation: Optional[RegulationResponse] = None
    source_reference: Optional[str] = None
    validity_period: Optional[str] = None
    confidence: float
    conditions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    nearest_alternatives: List[AlternativeLocation] = Field(default_factory=list)


class MapRegulationItem(BaseModel):
    """Map display item with standard color system coding."""
    id: str
    latitude: float
    longitude: float
    street_name: str
    street_side: str
    regulation_type: str
    sign_text: Optional[str] = None
    status_color: str  # RED, GREEN, ORANGE, BLUE, GRAY
    legal_status: EvaluationDecision
    operating_hours: Optional[str] = None
    verification_status: str = "VERIFIED"


class MapLoadingZoneItem(BaseModel):
    """Map item representing verified commercial and truck loading zones."""
    id: str
    latitude: float
    longitude: float
    street_name: str
    street_side: str
    zone_type: str  # COMMERCIAL_LOADING, TRUCK_LOADING, etc.
    max_duration_minutes: int = 180
    allowed_vehicles: List[str] = Field(default_factory=lambda: ["TRUCK", "COMMERCIAL_VAN"])
    verification_status: str = "VERIFIED"


class MapTruckRouteItem(BaseModel):
    """Map polyline segment representing designated NYC truck routes."""
    route_id: str
    street_name: str
    route_type: str  # 'Through' or 'Local'
    borough: str
    coordinates: Optional[Any] = None
