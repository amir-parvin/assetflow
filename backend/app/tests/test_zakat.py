import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_zakat_calculate(auth_client: AsyncClient):
    # Create assets
    await auth_client.post("/accounts", json={
        "name": "Savings", "type": "asset", "category": "bank", "balance": 10000,
    })
    await auth_client.post("/investments/stocks", json={
        "ticker": "MSFT", "name": "Microsoft", "shares": 20, "avg_cost": 300, "current_price": 400,
    })

    resp = await auth_client.post("/zakat/calculate", json={
        "gold_price_per_gram": 75.0,
        "use_gold_nisab": True,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["breakdown"]["cash_and_bank"] == 10000
    assert data["breakdown"]["investments"] == 8000  # 20 * 400
    assert data["breakdown"]["is_above_nisab"] is True
    assert data["breakdown"]["zakat_due"] > 0
    assert data["rate"] == 0.025
