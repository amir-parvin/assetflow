import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_account(auth_client: AsyncClient):
    resp = await auth_client.post("/accounts", json={
        "name": "Savings", "type": "asset", "category": "bank", "balance": 5000,
    })
    assert resp.status_code == 201
    assert resp.json()["name"] == "Savings"


@pytest.mark.asyncio
async def test_list_accounts(auth_client: AsyncClient):
    await auth_client.post("/accounts", json={
        "name": "Checking", "type": "asset", "category": "bank", "balance": 1000,
    })
    resp = await auth_client.get("/accounts")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_update_account(auth_client: AsyncClient):
    create = await auth_client.post("/accounts", json={
        "name": "Old", "type": "asset", "category": "cash", "balance": 100,
    })
    aid = create.json()["id"]
    resp = await auth_client.put(f"/accounts/{aid}", json={"name": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_account(auth_client: AsyncClient):
    create = await auth_client.post("/accounts", json={
        "name": "Del", "type": "liability", "category": "loan", "balance": 500,
    })
    aid = create.json()["id"]
    resp = await auth_client.delete(f"/accounts/{aid}")
    assert resp.status_code == 204
