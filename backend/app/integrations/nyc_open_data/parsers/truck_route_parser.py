"""Parser for NYC Truck Routes Network (Dataset spax-mybh)."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class NYCTruckRouteSegment(BaseModel):
    """Normalized segment from the NYC Truck Route network."""
    route_id: str
    street_name: str
    route_type: str  # 'Through' or 'Local'
    borough: str
    from_street: Optional[str] = None
    to_street: Optional[str] = None
    geometry: Optional[Any] = None


class NYCTruckRouteParser:
    """Parses raw NYC DOT Truck Route network features."""

    @classmethod
    def parse_record(cls, raw: Dict[str, Any]) -> NYCTruckRouteSegment:
        street = raw.get("street", raw.get("street_name", "UNKNOWN ROAD"))
        route_type = raw.get("route_type", raw.get("taz_type", "Local"))
        borough = raw.get("borough", "MANHATTAN")

        return NYCTruckRouteSegment(
            route_id=str(raw.get("segment_id", raw.get("nodeid", "truck-route"))),
            street_name=street,
            route_type=route_type,
            borough=borough,
            from_street=raw.get("from_street"),
            to_street=raw.get("to_street"),
            geometry=raw.get("the_geom"),
        )
