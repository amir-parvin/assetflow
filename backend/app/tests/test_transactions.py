import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_transaction(auth_client: AsyncClient):
    acct = await auth_client.post("/accounts", json={
        "name": "Main", "type": "asset", "category": "bank", "balance": 1000,
    })
    aid = acct.json()["id"]
    resp = await auth_client.post("/transactions", json={
        "account_id": aid, "amount": 500, "type": "income",
        "category": "salary", "date": "2024-01-15",
    })
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_list_transactions_filtered(auth_client: AsyncClient):
    acct = await auth_client.post("/accounts", json={
        "name": "Filter", "type": "asset", "category": "bank", "balance": 0,
    })
    aid = acct.json()["id"]
    await auth_client.post("/transactions", json={
        "account_id": aid, "amount": 100, "type": "expense",
        "category": "food", "date": "2024-02-01",
    })
    await auth_client.post("/transactions", json={
        "account_id": aid, "amount": 200, "type": "income",
        "category": "freelance", "date": "2024-02-05",
    })
    resp = await auth_client.get("/transactions?type=income")
    assert resp.status_code == 200
    for t in resp.json():
        assert t["type"] == "income"
