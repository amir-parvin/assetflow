import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_stock_crud(auth_client: AsyncClient):
    resp = await auth_client.post("/investments/stocks", json={
        "ticker": "AAPL", "name": "Apple", "shares": 10, "avg_cost": 150, "current_price": 180,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["market_value"] == 1800
    assert data["gain_loss"] == 300

    resp = await auth_client.get("/investments/stocks")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    sid = data["id"]
    resp = await auth_client.put(f"/investments/stocks/{sid}", json={"current_price": 200})
    assert resp.json()["market_value"] == 2000

    resp = await auth_client.delete(f"/investments/stocks/{sid}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_real_estate_crud(auth_client: AsyncClient):
    resp = await auth_client.post("/investments/real-estate", json={
        "name": "Apt 1", "location": "NYC", "property_type": "apartment",
        "estimated_value": 500000, "monthly_rent": 2000,
    })
    assert resp.status_code == 201
    assert resp.json()["annual_rent"] == 24000


@pytest.mark.asyncio
async def test_business_crud(auth_client: AsyncClient):
    resp = await auth_client.post("/investments/business", json={
        "name": "Startup", "equity_percent": 25,
        "invested_value": 50000, "current_value": 80000, "annual_income": 10000,
    })
    assert resp.status_code == 201
    assert resp.json()["gain_loss"] == 30000


@pytest.mark.asyncio
async def test_portfolio_summary(auth_client: AsyncClient):
    await auth_client.post("/investments/stocks", json={
        "ticker": "GOOG", "name": "Google", "shares": 5, "avg_cost": 100, "current_price": 150,
    })
    resp = await auth_client.get("/investments/portfolio")
    assert resp.status_code == 200
    assert "total_portfolio_value" in resp.json()
