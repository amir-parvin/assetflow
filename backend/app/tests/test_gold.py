import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_gold_syncs_to_segment(auth_client: AsyncClient):
    """Create gold holding -> auto-syncs to Gold segment with correct balance."""
    resp = await auth_client.post("/investments/gold", json={
        "name": "Wedding Gold",
        "weight": 10,
        "weight_unit": "vori",
        "purchase_price_per_vori": 100000,
        "current_price_per_vori": 120000,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["weight_vori"] == 10
    assert data["current_value"] == 10 * 120000
    assert data["gain_loss"] == 10 * (120000 - 100000)

    # Verify Gold segment exists and has correct balance
    purse = await auth_client.get("/accounts/purse")
    segments = purse.json()
    gold_seg = next(s for s in segments if s["category"] == "gold")
    assert gold_seg["total_balance"] == 10 * 120000


@pytest.mark.asyncio
async def test_update_price_updates_balance(auth_client: AsyncClient):
    """Update current_price_per_vori -> segment balance updates."""
    resp = await auth_client.post("/investments/gold", json={
        "name": "Savings Gold",
        "weight": 5,
        "weight_unit": "vori",
        "purchase_price_per_vori": 100000,
        "current_price_per_vori": 100000,
    })
    gold_id = resp.json()["id"]

    # Update price
    resp = await auth_client.put(f"/investments/gold/{gold_id}", json={
        "current_price_per_vori": 150000,
    })
    assert resp.status_code == 200
    assert resp.json()["current_value"] == 5 * 150000

    # Verify segment balance updated
    purse = await auth_client.get("/accounts/purse")
    gold_seg = next(s for s in purse.json() if s["category"] == "gold")
    assert gold_seg["total_balance"] == 5 * 150000


@pytest.mark.asyncio
async def test_delete_removes_from_segment(auth_client: AsyncClient):
    """Delete gold holding -> removed from Gold segment."""
    resp = await auth_client.post("/investments/gold", json={
        "name": "Old Jewelry",
        "weight": 3,
        "weight_unit": "vori",
        "purchase_price_per_vori": 80000,
        "current_price_per_vori": 90000,
    })
    gold_id = resp.json()["id"]

    await auth_client.delete(f"/investments/gold/{gold_id}")

    purse = await auth_client.get("/accounts/purse")
    gold_seg = next(s for s in purse.json() if s["category"] == "gold")
    assert gold_seg["total_balance"] == 0
    assert len(gold_seg["sub_segments"]) == 0


@pytest.mark.asyncio
async def test_weight_in_grams(auth_client: AsyncClient):
    """Weight in grams is converted to vori correctly."""
    # 11.664 grams = 1 vori
    grams = 11.664 * 2  # 2 vori worth of grams
    resp = await auth_client.post("/investments/gold", json={
        "name": "Gram Gold",
        "weight": grams,
        "weight_unit": "gram",
        "purchase_price_per_vori": 100000,
        "current_price_per_vori": 100000,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert abs(data["weight_vori"] - 2.0) < 0.01
    assert abs(data["current_value"] - 200000) < 100
