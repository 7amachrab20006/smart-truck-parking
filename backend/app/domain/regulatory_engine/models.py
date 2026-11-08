"""Domain models and value objects for the Regulatory Intelligence Engine."""

from datetime import datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RequestedActivity(str, Enum):
    """Activity requested by the driver/vehicle."""
    PASS_THROUGH = "PASS_THROUGH"
    STOP = "STOP"
    PARK = "PARK"
    LOAD = "LOAD"
    UNLOAD = "UNLOAD"


class EvaluationDecision(str, Enum):
    """Outcome of regulatory evaluation."""
    ALLOWED = "ALLOWED"
    PROHIBITED = "PROHIBITED"
    CONDITIONAL = "CONDITIONAL"
    UNKNOWN = "UNKNOWN"


class StreetSide(str, Enum):
    """Side of the roadway relative to heading or cardinal orientation."""
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BOTH = "BOTH"
    UNKNOWN = "UNKNOWN"


class RegulationClassification(str, Enum):
    """Legal classification of a restriction or regulation."""
    NO_PARKING = "NO_PARKING"
    NO_STANDING = "NO_STANDING"
    NO_STOPPING = "NO_STOPPING"
    LOADING_ONLY = "LOADING_ONLY"
    TRUCK_LOADING_ONLY = "TRUCK_LOADING_ONLY"
    COMMERCIAL_LOADING = "COMMERCIAL_LOADING"
    METERED_PARKING = "METERED_PARKING"
    TRUCK_ROUTE_RESTRICTION = "TRUCK_ROUTE_RESTRICTION"
    HEIGHT_RESTRICTION = "HEIGHT_RESTRICTION"
    WEIGHT_RESTRICTION = "WEIGHT_RESTRICTION"
    WIDTH_RESTRICTION = "WIDTH_RESTRICTION"
    LENGTH_RESTRICTION = "LENGTH_RESTRICTION"
    TEMPORARY_RESTRICTION = "TEMPORARY_RESTRICTION"


class VehicleProfile(BaseModel):
    """Vehicle specifications utilized during restriction evaluation."""
    vehicle_id: Optional[str] = None
    vehicle_type: str = "DELIVERY_VAN"
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    height_m: Optional[float] = None
    gvwr_kg: Optional[float] = None
    operating_weight_kg: Optional[float] = None
    axle_count: Optional[int] = 2
    has_trailer: bool = False
    is_commercial: bool = True
    is_hazmat: bool = False
    permits: List[str] = Field(default_factory=list)


class TimeRule(BaseModel):
    """Temporal schedule constraints for a regulation."""
    days_of_week: List[int] = Field(default_factory=list)  # 0=Monday, 6=Sunday (or 0=Sun per adapter)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    max_duration_minutes: Optional[int] = None
    is_overnight: bool = False


class RegulationRecord(BaseModel):
    """Normalized regulatory record passed to the engine."""
    id: str
    jurisdiction_code: str = "US-NYC"
    classification: RegulationClassification
    street_name: str
    street_side: StreetSide = StreetSide.UNKNOWN
    sign_text: Optional[str] = None
    time_rules: List[TimeRule] = Field(default_factory=list)
    max_height_m: Optional[float] = None
    max_weight_kg: Optional[float] = None
    max_width_m: Optional[float] = None
    max_length_m: Optional[float] = None
    applies_to_vehicle_types: Optional[List[str]] = None
    is_commercial_only: bool = False
    is_temporary: bool = False
    effective_start: Optional[datetime] = None
    effective_end: Optional[datetime] = None
    data_source: str = "NYC DOT SIMS"
    confidence_score: float = 1.0
    verification_status: str = "VERIFIED"


class RuleEvaluationResult(BaseModel):
    """Detailed evaluation from a jurisdiction adapter."""
    decision: EvaluationDecision
    explanation: str
    applicable_regulation_id: Optional[str] = None
    applicable_regulation_type: Optional[str] = None
    max_permitted_duration_minutes: Optional[int] = None
    conditions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    source_reference: Optional[str] = None
    confidence_score: float = 1.0


class AlternativeLocation(BaseModel):
    """Nearby legally compliant loading or parking suggestion."""
    name: str
    address: str
    location_type: str
    distance_meters: float
    max_duration_minutes: Optional[int] = None
    legal_status: EvaluationDecision = EvaluationDecision.ALLOWED


class RegulatoryEvaluationResponse(BaseModel):
    """Consolidated response payload for regulatory inquiries."""
    decision: EvaluationDecision
    explanation: str
    applicable_regulation: Optional[RegulationRecord] = None
    source_reference: Optional[str] = None
    validity_period: Optional[str] = None
    confidence: float = 1.0
    relevant_restrictions: List[str] = Field(default_factory=list)
    nearest_alternatives: List[AlternativeLocation] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
