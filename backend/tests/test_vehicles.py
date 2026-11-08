"""Tests for vehicle CRUD endpoints and unit conversions."""

import uuid
import pytest
from httpx import AsyncClient
from app.core.security import create_access_token, hash_password
from app.models.user import User, UserRole


@pytest.fixture
async def second_user(db_session) -> User:
    """Create a second distinct user to test authorization boundaries."""
    user = User(
        email="second@example.com",
        password_hash=hash_password("Password999!"),
        first_name="Second",
        last_name="Driver",
        role=UserRole.DRIVER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def second_auth_headers(second_user: User) -> dict:
    """Auth headers for second user."""
    token = create_access_token(
        subject=str(second_user.id),
        role=second_user.role.value if hasattr(second_user.role, "value") else str(second_user.role),
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_vehicle_metric(client: AsyncClient, auth_headers: dict):
    """Test creating vehicle using metric measurements."""
    payload = {
        "registration_id": "NY-TRUCK-101",
        "manufacturer": "Freightliner",
        "model_name": "Cascadia",
        "year": 2023,
        "vehicle_type": "SEMI_TRUCK",
        "length_m": 16.5,
        "width_m": 2.6,
        "height_m": 4.1,
        "gvwr_kg": 36287.0,
        "operating_weight_kg": 15000.0,
        "axle_count": 5,
        "has_trailer": True,
        "trailer_type": "DRY_VAN_53FT",
        "trailer_length_m": 16.15,
        "is_commercial": True,
    }
    response = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["registration_id"] == "NY-TRUCK-101"
    assert data["length_m"] == 16.5
    assert data["height_m"] == 4.1
    assert data["length_ft"] is not None
    assert data["height_ft"] is not None
    assert data["gvwr_lbs"] is not None
    assert "id" in data


@pytest.mark.asyncio
async def test_create_vehicle_imperial_conversion(client: AsyncClient, auth_headers: dict):
    """Test creating vehicle providing imperial units which convert to metric."""
    payload = {
        "registration_id": "VAN-99",
        "manufacturer": "Ford",
        "model_name": "Transit 250",
        "year": 2022,
        "vehicle_type": "DELIVERY_VAN",
        "length_ft": 20.0,   # ~6.10 meters
        "width_ft": 7.0,    # ~2.13 meters
        "height_ft": 9.0,   # ~2.74 meters
        "gvwr_lbs": 9070.0, # ~4114 kg
        "is_commercial": True,
    }
    response = await client.post("/api/v1/vehicles", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["registration_id"] == "VAN-99"
    assert data["length_m"] is not None
    assert abs(data["length_m"] - 6.10) < 0.1
    assert abs(data["height_m"] - 2.74) < 0.1


@pytest.mark.asyncio
async def test_list_vehicles(client: AsyncClient, auth_headers: dict):
    """Test listing user vehicles returns paginated list."""
    # Create two vehicles
    for reg in ["BOX-1", "BOX-2"]:
        await client.post(
            "/api/v1/vehicles",
            json={
                "registration_id": reg,
                "vehicle_type": "BOX_TRUCK",
                "length_m": 8.0,
            },
            headers=auth_headers,
        )

    response = await client.get("/api/v1/vehicles?page=1&page_size=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_get_vehicle_by_id(client: AsyncClient, auth_headers: dict):
    """Test retrieving a specific vehicle by UUID."""
    create_resp = await client.post(
        "/api/v1/vehicles",
        json={"registration_id": "GET-TEST", "vehicle_type": "STRAIGHT_TRUCK"},
        headers=auth_headers,
    )
    vehicle_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/vehicles/{vehicle_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == vehicle_id
    assert get_resp.json()["registration_id"] == "GET-TEST"


@pytest.mark.asyncio
async def test_update_vehicle(client: AsyncClient, auth_headers: dict):
    """Test modifying vehicle attributes and dimensions."""
    create_resp = await client.post(
        "/api/v1/vehicles",
        json={"registration_id": "UPDATE-ME", "vehicle_type": "BOX_TRUCK", "height_m": 3.0},
        headers=auth_headers,
    )
    vehicle_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/v1/vehicles/{vehicle_id}",
        json={"height_m": 3.5, "model_name": "Updated Model"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["height_m"] == 3.5
    assert update_resp.json()["model_name"] == "Updated Model"


@pytest.mark.asyncio
async def test_delete_vehicle(client: AsyncClient, auth_headers: dict):
    """Test deleting a vehicle removes it from list and retrieval."""
    create_resp = await client.post(
        "/api/v1/vehicles",
        json={"registration_id": "DELETE-ME", "vehicle_type": "DELIVERY_VAN"},
        headers=auth_headers,
    )
    vehicle_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/vehicles/{vehicle_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Retrieve should return 404
    get_resp = await client.get(f"/api/v1/vehicles/{vehicle_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_vehicle_unauthorized_access(
    client: AsyncClient,
    auth_headers: dict,
    second_auth_headers: dict,
):
    """Test that one driver cannot access or modify another driver's vehicle."""
    # User 1 creates vehicle
    create_resp = await client.post(
        "/api/v1/vehicles",
        json={"registration_id": "USER1-TRUCK", "vehicle_type": "BOX_TRUCK"},
        headers=auth_headers,
    )
    vehicle_id = create_resp.json()["id"]

    # User 2 tries to fetch User 1's vehicle
    unauth_get = await client.get(f"/api/v1/vehicles/{vehicle_id}", headers=second_auth_headers)
    assert unauth_get.status_code == 403
    assert unauth_get.json()["error"]["code"] == "VEHICLE_ACCESS_DENIED"

    # User 2 tries to update User 1's vehicle
    unauth_put = await client.put(
        f"/api/v1/vehicles/{vehicle_id}",
        json={"registration_id": "HIJACKED"},
        headers=second_auth_headers,
    )
    assert unauth_put.status_code == 403

    # User 2 tries to delete User 1's vehicle
    unauth_del = await client.delete(f"/api/v1/vehicles/{vehicle_id}", headers=second_auth_headers)
    assert unauth_del.status_code == 403
