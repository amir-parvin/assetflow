import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "pass123",
        "full_name": "New User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    payload = {"email": "dup@example.com", "password": "pass123", "full_name": "Dup"}
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "pass123",
        "full_name": "Login User",
    })
    resp = await client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "pass123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_bad_password(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "bad@example.com",
        "password": "pass123",
        "full_name": "Bad",
    })
    resp = await client.post("/auth/login", json={
        "email": "bad@example.com",
        "password": "wrong",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me(auth_client: AsyncClient):
    resp = await auth_client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_refresh(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "refresh@example.com",
        "password": "pass123",
        "full_name": "Refresh",
    })
    login_resp = await client.post("/auth/login", json={
        "email": "refresh@example.com",
        "password": "pass123",
    })
    refresh_token = login_resp.json()["refresh_token"]
    resp = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
