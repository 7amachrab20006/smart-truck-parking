"""Tests for authentication and user management endpoints."""

import pytest
from httpx import AsyncClient
from app.models.user import User


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    """Test successful user registration."""
    payload = {
        "email": "newdriver@example.com",
        "password": "StrongPassword123!",
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "+12125550188",
        "role": "DRIVER",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newdriver@example.com"
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["role"] == "DRIVER"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user: User):
    """Test that registering an existing email returns 409 Conflict."""
    payload = {
        "email": test_user.email,
        "password": "AnotherPassword123!",
        "first_name": "Duplicate",
        "last_name": "User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_register_invalid_data(client: AsyncClient):
    """Test registration validation error on short password and bad email."""
    payload = {
        "email": "not-an-email",
        "password": "short",
        "first_name": "",
        "last_name": "Doe",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "REQUEST_VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login returns access and refresh tokens."""
    payload = {
        "email": test_user.email,
        "password": "SecurePassword123!",
        "device_info": "Test Runner",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user: User):
    """Test login with incorrect password returns 401."""
    payload = {
        "email": test_user.email,
        "password": "WrongPassword!",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_refresh_token_flow(client: AsyncClient, test_user: User):
    """Test refreshing an access token using a valid refresh token."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )
    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]

    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200
    refreshed_data = refresh_resp.json()
    assert "access_token" in refreshed_data
    assert "refresh_token" in refreshed_data
    assert refreshed_data["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test fetching authenticated user profile."""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_update_current_user_profile(client: AsyncClient, auth_headers: dict):
    """Test updating authenticated user profile details."""
    payload = {
        "first_name": "Johnny",
        "last_name": "Updated",
        "phone": "+19998887777",
    }
    response = await client.put("/api/v1/auth/me", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Johnny"
    assert data["last_name"] == "Updated"
    assert data["phone"] == "+19998887777"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected route without token returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOT_AUTHENTICATED"


@pytest.mark.asyncio
async def test_logout_flow(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test logging out revokes refresh token."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    logout_resp = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers=auth_headers,
    )
    assert logout_resp.status_code == 200
    assert logout_resp.json()["success"] is True

    # Trying to refresh revoked token should fail
    fail_refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert fail_refresh.status_code == 401
