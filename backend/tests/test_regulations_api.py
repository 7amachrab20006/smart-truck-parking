"""Integration and API tests for NYC data parsers and regulations/map REST endpoints."""

from datetime import time
import pytest
from httpx import AsyncClient

from app.domain.regulatory_engine.models import RegulationClassification, StreetSide
from app.integrations.nyc_open_data import NYCLowBridgeParser, NYCSignParser


def test_nyc_sign_parser_classifications():
    """Verifies SIMS parking sign text parsing into proper legal classifications."""
    # No Parking
    p1 = NYCSignParser.parse_classification("NO PARKING 8AM-6PM MON THRU FRI")
    assert p1 == RegulationClassification.NO_PARKING

    # No Standing
    p2 = NYCSignParser.parse_classification("NO STANDING ANYTIME")
    assert p2 == RegulationClassification.NO_STANDING

    # No Stopping
    p3 = NYCSignParser.parse_classification("NO STOPPING 7AM-9AM")
    assert p3 == RegulationClassification.NO_STOPPING

    # Truck Loading
    p4 = NYCSignParser.parse_classification("NO STANDING EXCEPT TRUCKS LOADING & UNLOADING 7AM-7PM")
    assert p4 == RegulationClassification.TRUCK_LOADING_ONLY

    # Commercial Metered
    p5 = NYCSignParser.parse_classification("COMMERCIAL METERED PARKING 3 HR LIMIT 7AM-6PM")
    assert p5 == RegulationClassification.COMMERCIAL_LOADING


def test_nyc_sign_parser_time_windows():
    """Verifies parsing of standard and overnight time windows."""
    s1, e1, o1 = NYCSignParser.parse_time_window("NO PARKING 8AM-6PM MON THRU FRI")
    assert s1 == time(8, 0)
    assert e1 == time(18, 0)
    assert o1 is False

    # Overnight window
    s2, e2, o2 = NYCSignParser.parse_time_window("NO STANDING 10PM-6AM")
    assert s2 == time(22, 0)
    assert e2 == time(6, 0)
    assert o2 is True


def test_nyc_low_bridge_parser():
    """Verifies conversion of low bridge clearance from feet/inches to meters."""
    raw = {
        "bin": "2240010",
        "highway": "FDR DRIVE",
        "cross_street": "E 14TH ST OVERPASS",
        "clearance_feet": "11",
        "clearance_inches": "6",
    }
    reg = NYCLowBridgeParser.parse_record(raw)
    assert reg.classification == RegulationClassification.HEIGHT_RESTRICTION
    # 11 ft 6 in = 138 inches = 3.5052 meters
    assert abs(reg.max_height_m - 3.5052) < 0.01


@pytest.mark.asyncio
async def test_evaluate_regulation_api(client: AsyncClient):
    """Verifies POST /api/v1/regulations/evaluate endpoint."""
    payload = {
        "latitude": 40.7580,
        "longitude": -73.9855,
        "activity": "PARK",
        "vehicle_type": "BOX_TRUCK",
        "is_commercial": True,
        "street_name": "Broadway",
        "street_side": "RIGHT",
    }
    response = await client.post("/api/v1/regulations/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "decision" in data["data"]
    assert "explanation" in data["data"]
    assert "status_color" in data["data"]
    assert len(data["data"]["nearest_alternatives"]) > 0


@pytest.mark.asyncio
async def test_get_map_regulations_api(client: AsyncClient):
    """Verifies GET /api/v1/map/regulations endpoint."""
    response = await client.get("/api/v1/map/regulations?latitude=40.7580&longitude=-73.9855")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 4
    for item in data["data"]:
        assert "status_color" in item
        assert "legal_status" in item
        assert "street_name" in item


@pytest.mark.asyncio
async def test_get_map_loading_zones_api(client: AsyncClient):
    """Verifies GET /api/v1/map/loading-zones endpoint."""
    response = await client.get("/api/v1/map/loading-zones?borough=MANHATTAN")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 3
    assert all("zone_type" in z for z in data["data"])


@pytest.mark.asyncio
async def test_get_map_truck_routes_api(client: AsyncClient):
    """Verifies GET /api/v1/map/truck-routes endpoint."""
    response = await client.get("/api/v1/map/truck-routes?borough=MANHATTAN")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 4
    assert any(r["route_type"] == "Through" for r in data["data"])
    assert any(r["route_type"] == "Local" for r in data["data"])
