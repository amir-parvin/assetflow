from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.report import (
    BalanceSheetReport, BalanceSheetItem,
    IncomeExpenseReport,
    CashFlowReport, CashFlowPoint,
    DashboardSummary,
    NetWorthReport, NetWorthPoint,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/net-worth", response_model=NetWorthReport)
async def net_worth(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Account).where(Account.user_id == current_user.id, Account.is_active == True))
    accounts = result.scalars().all()
    assets = sum(float(a.balance) for a in accounts if a.type == "asset")
    liabilities = sum(float(a.balance) for a in accounts if a.type == "liability")
    nw = assets - liabilities

    return NetWorthReport(
        current_net_worth=nw,
        history=[NetWorthPoint(date=date.today().isoformat(), assets=assets, liabilities=liabilities, net_worth=nw)],
    )


@router.get("/balance-sheet", response_model=BalanceSheetReport)
async def balance_sheet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Account).where(Account.user_id == current_user.id, Account.is_active == True))
    accounts = result.scalars().all()

    asset_cats: dict[str, list] = {}
    liability_cats: dict[str, list] = {}

    for a in accounts:
        bucket = asset_cats if a.type == "asset" else liability_cats if a.type == "liability" else None
        if bucket is not None:
            bucket.setdefault(a.category, []).append({"name": a.name, "balance": float(a.balance)})

    total_assets = sum(float(a.balance) for a in accounts if a.type == "asset")
    total_liabilities = sum(float(a.balance) for a in accounts if a.type == "liability")

    return BalanceSheetReport(
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=total_assets - total_liabilities,
        assets=[BalanceSheetItem(category=k, total=sum(x["balance"] for x in v), accounts=v) for k, v in asset_cats.items()],
        liabilities=[BalanceSheetItem(category=k, total=sum(x["balance"] for x in v), accounts=v) for k, v in liability_cats.items()],
    )


@router.get("/income-expense", response_model=IncomeExpenseReport)
async def income_expense(
    months: int = 1,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = date.today() - timedelta(days=months * 30)
    result = await db.execute(
        select(Transaction).where(
            Transaction.user_id == current_user.id,
            Transaction.date >= start,
        )
    )
    txns = result.scalars().all()
    income = sum(float(t.amount) for t in txns if t.type == "income")
    expense = sum(float(t.amount) for t in txns if t.type == "expense")

    cats: dict[str, dict] = {}
    for t in txns:
        cats.setdefault(t.category, {"category": t.category, "income": 0, "expense": 0})
        if t.type == "income":
            cats[t.category]["income"] += float(t.amount)
        elif t.type == "expense":
            cats[t.category]["expense"] += float(t.amount)

    return IncomeExpenseReport(
        period=f"Last {months} month(s)",
        total_income=income,
        total_expense=expense,
        net=income - expense,
        by_category=list(cats.values()),
    )


@router.get("/cash-flow", response_model=CashFlowReport)
async def cash_flow(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = date.today() - timedelta(days=months * 30)
    result = await db.execute(
        select(Transaction).where(
            Transaction.user_id == current_user.id,
            Transaction.date >= start,
        ).order_by(Transaction.date)
    )
    txns = result.scalars().all()

    monthly: dict[str, dict] = {}
    for t in txns:
        key = t.date.strftime("%Y-%m")
        monthly.setdefault(key, {"inflow": 0, "outflow": 0})
        if t.type == "income":
            monthly[key]["inflow"] += float(t.amount)
        elif t.type == "expense":
            monthly[key]["outflow"] += float(t.amount)

    data = [
        CashFlowPoint(period=k, inflow=v["inflow"], outflow=v["outflow"], net=v["inflow"] - v["outflow"])
        for k, v in sorted(monthly.items())
    ]

    return CashFlowReport(data=data)


@router.get("/dashboard", response_model=DashboardSummary)
async def dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    accts = await db.execute(select(Account).where(Account.user_id == current_user.id, Account.is_active == True))
    accounts = accts.scalars().all()
    total_assets = sum(float(a.balance) for a in accounts if a.type == "asset")
    total_liabilities = sum(float(a.balance) for a in accounts if a.type == "liability")

    start = date.today() - timedelta(days=30)
    txns_result = await db.execute(
        select(Transaction).where(Transaction.user_id == current_user.id, Transaction.date >= start)
        .order_by(Transaction.date.desc())
    )
    txns = txns_result.scalars().all()
    monthly_income = sum(float(t.amount) for t in txns if t.type == "income")
    monthly_expense = sum(float(t.amount) for t in txns if t.type == "expense")

    recent = await db.execute(
        select(Transaction).where(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.desc()).limit(5)
    )
    recent_txns = [
        {"id": t.id, "amount": float(t.amount), "type": t.type, "category": t.category, "date": t.date.isoformat(), "description": t.description}
        for t in recent.scalars().all()
    ]

    allocation: dict[str, float] = {}
    for a in accounts:
        if a.type == "asset":
            allocation[a.category] = allocation.get(a.category, 0) + float(a.balance)
    alloc_list = [{"category": k, "value": v} for k, v in allocation.items()]

    return DashboardSummary(
        net_worth=total_assets - total_liabilities,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        recent_transactions=recent_txns,
        asset_allocation=alloc_list,
    )
