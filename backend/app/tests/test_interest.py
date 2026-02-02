import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_record_interest_increases_fund_balance(auth_client: AsyncClient):
    """Recording interest should increase the interest fund liability balance."""
    resp = await auth_client.post("/interest", json={
        "amount": 150.00,
        "source": "Bank ABC",
        "date": "2025-06-15T00:00:00Z",
        "fiscal_year": 2025,
    })
    assert resp.status_code == 201
    assert resp.json()["status"] == "received"

    await auth_client.post("/interest", json={
        "amount": 50.00,
        "source": "Bond XYZ",
        "date": "2025-07-01T00:00:00Z",
        "fiscal_year": 2025,
    })

    summary = await auth_client.get("/interest/fund-summary")
    assert summary.status_code == 200
    data = summary.json()
    assert float(data["total_received"]) == 200.00
    assert float(data["undistributed_balance"]) == 200.00


@pytest.mark.asyncio
async def test_mark_distributed_decreases_fund(auth_client: AsyncClient):
    """Marking an entry as distributed should decrease undistributed balance."""
    resp1 = await auth_client.post("/interest", json={
        "amount": 300.00,
        "source": "Bank ABC",
        "date": "2025-06-15T00:00:00Z",
        "fiscal_year": 2025,
    })
    entry1_id = resp1.json()["id"]

    await auth_client.post("/interest", json={
        "amount": 100.00,
        "source": "Bond XYZ",
        "date": "2025-07-01T00:00:00Z",
        "fiscal_year": 2025,
    })

    # Mark first entry as distributed (given to charity)
    update_resp = await auth_client.put(f"/interest/{entry1_id}", json={
        "status": "distributed",
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "distributed"

    summary = await auth_client.get("/interest/fund-summary")
    data = summary.json()
    # Total ever received: 400, distributed: 300, undistributed: 100
    assert float(data["total_received"]) == 400.00
    assert float(data["total_distributed"]) == 300.00
    assert float(data["undistributed_balance"]) == 100.00


@pytest.mark.asyncio
async def test_fiscal_year_summary(auth_client: AsyncClient):
    """Fiscal year summary should correctly aggregate entries by year."""
    await auth_client.post("/interest", json={
        "amount": 200.00,
        "source": "Bank ABC",
        "date": "2025-03-01T00:00:00Z",
        "fiscal_year": 2025,
    })
    resp = await auth_client.post("/interest", json={
        "amount": 100.00,
        "source": "Bank ABC",
        "date": "2025-09-01T00:00:00Z",
        "fiscal_year": 2025,
    })
    await auth_client.put(f"/interest/{resp.json()['id']}", json={
        "status": "distributed",
    })

    await auth_client.post("/interest", json={
        "amount": 500.00,
        "source": "Old Bond",
        "date": "2024-06-01T00:00:00Z",
        "fiscal_year": 2024,
    })

    fy = await auth_client.get("/interest/fiscal-year/2025")
    assert fy.status_code == 200
    data = fy.json()
    assert data["fiscal_year"] == 2025
    assert float(data["total_received"]) == 300.00
    assert float(data["total_distributed"]) == 100.00
    assert float(data["undistributed"]) == 200.00
    assert data["entry_count"] == 2

    fy24 = await auth_client.get("/interest/fiscal-year/2024")
    data24 = fy24.json()
    assert float(data24["total_received"]) == 500.00
    assert float(data24["total_distributed"]) == 0.00
    assert data24["entry_count"] == 1


@pytest.mark.asyncio
async def test_undistributed_total_correct(auth_client: AsyncClient):
    """Undistributed total across all years should be correct and match account balance."""
    await auth_client.post("/interest", json={
        "amount": 1000.00,
        "source": "Bank A",
        "date": "2024-01-01T00:00:00Z",
        "fiscal_year": 2024,
    })
    resp2 = await auth_client.post("/interest", json={
        "amount": 500.00,
        "source": "Bank B",
        "date": "2025-01-01T00:00:00Z",
        "fiscal_year": 2025,
    })
    await auth_client.post("/interest", json={
        "amount": 250.00,
        "source": "Bank C",
        "date": "2025-06-01T00:00:00Z",
        "fiscal_year": 2025,
    })

    await auth_client.put(f"/interest/{resp2.json()['id']}", json={
        "status": "distributed",
    })

    summary = await auth_client.get("/interest/fund-summary")
    data = summary.json()
    assert float(data["total_received"]) == 1750.00
    assert float(data["total_distributed"]) == 500.00
    assert float(data["undistributed_balance"]) == 1250.00

    # Verify undistributed entries sum matches balance
    entries = await auth_client.get("/interest", params={"status": "received"})
    assert entries.status_code == 200
    received_entries = entries.json()
    received_sum = sum(float(e["amount"]) for e in received_entries)
    assert received_sum == 1250.00

    # Verify distributed entries
    dist_entries = await auth_client.get("/interest", params={"status": "distributed"})
    dist_sum = sum(float(e["amount"]) for e in dist_entries.json())
    assert dist_sum == 500.00
