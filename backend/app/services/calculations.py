from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.transaction import Transaction


async def get_leaf_accounts(user_id: int, db: AsyncSession) -> list[Account]:
    """Get all active, non-segment (leaf) accounts for a user."""
    result = await db.execute(
        select(Account).where(
            Account.user_id == user_id,
            Account.is_active == True,
            Account.is_segment == False,
        )
    )
    return list(result.scalars().all())


async def get_total_assets(user_id: int, db: AsyncSession) -> float:
    accounts = await get_leaf_accounts(user_id, db)
    return sum(float(a.balance) for a in accounts if a.type == "asset")


async def get_total_liabilities(user_id: int, db: AsyncSession) -> float:
    accounts = await get_leaf_accounts(user_id, db)
    return sum(float(a.balance) for a in accounts if a.type == "liability")


async def get_net_worth(user_id: int, db: AsyncSession) -> tuple[float, float, float]:
    """Returns (net_worth, total_assets, total_liabilities)."""
    accounts = await get_leaf_accounts(user_id, db)
    assets = sum(float(a.balance) for a in accounts if a.type == "asset")
    liabilities = sum(float(a.balance) for a in accounts if a.type == "liability")
    return assets - liabilities, assets, liabilities


async def get_monthly_income_expense(
    user_id: int, db: AsyncSession, months: int = 1
) -> tuple[float, float]:
    """Returns (monthly_income, monthly_expense)."""
    start = date.today() - timedelta(days=months * 30)
    result = await db.execute(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.date >= start,
        )
    )
    txns = result.scalars().all()
    income = sum(float(t.amount) for t in txns if t.type == "income")
    expense = sum(float(t.amount) for t in txns if t.type == "expense")
    return income, expense


async def get_asset_allocation(user_id: int, db: AsyncSession) -> list[dict]:
    accounts = await get_leaf_accounts(user_id, db)
    allocation: dict[str, float] = {}
    for a in accounts:
        if a.type == "asset":
            allocation[a.category] = allocation.get(a.category, 0) + float(a.balance)
    return [{"category": k, "value": v} for k, v in allocation.items()]


async def get_liability_allocation(user_id: int, db: AsyncSession) -> list[dict]:
    accounts = await get_leaf_accounts(user_id, db)
    allocation: dict[str, float] = {}
    for a in accounts:
        if a.type == "liability":
            allocation[a.category] = allocation.get(a.category, 0) + float(a.balance)
    return [{"category": k, "value": v} for k, v in allocation.items()]
