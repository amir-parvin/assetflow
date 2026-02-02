from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.interest import InterestEntry
from app.models.account import Account
from app.models.user import User
from app.schemas.interest import (
    InterestEntryCreate,
    InterestEntryUpdate,
    InterestEntryResponse,
    InterestFundSummary,
    FiscalYearSummary,
)
from app.api.accounts import get_or_create_segment, recalculate_segment_balance

router = APIRouter(prefix="/interest", tags=["interest"])

INTEREST_FUND_NAME = "Interest Fund (Liability)"


async def get_or_create_interest_fund(user_id: int, db: AsyncSession) -> Account:
    """Get or create the interest fund liability account."""
    result = await db.execute(
        select(Account).where(
            Account.user_id == user_id,
            Account.name == INTEREST_FUND_NAME,
            Account.type == "liability",
            Account.category == "liability",
            Account.is_segment == False,
        )
    )
    fund = result.scalar_one_or_none()
    if fund:
        return fund

    segment = await get_or_create_segment(user_id, "liability", db)
    fund = Account(
        user_id=user_id,
        parent_id=segment.id,
        name=INTEREST_FUND_NAME,
        type="liability",
        category="liability",
        balance=0,
        currency="USD",
    )
    db.add(fund)
    await db.commit()
    await db.refresh(fund)
    return fund


async def sync_fund_balance(user_id: int, db: AsyncSession):
    """Recalculate interest fund balance = sum of undistributed entries."""
    undistributed = await db.execute(
        select(func.coalesce(func.sum(InterestEntry.amount), 0)).where(
            InterestEntry.user_id == user_id,
            InterestEntry.status == "received",
        )
    )
    fund = await get_or_create_interest_fund(user_id, db)
    fund.balance = float(undistributed.scalar())
    await db.commit()

    if fund.parent_id:
        await recalculate_segment_balance(fund.parent_id, db)


@router.get("", response_model=list[InterestEntryResponse])
async def list_interest_entries(
    fiscal_year: int | None = None,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(InterestEntry).where(InterestEntry.user_id == current_user.id)
    if fiscal_year:
        query = query.where(InterestEntry.fiscal_year == fiscal_year)
    if status:
        query = query.where(InterestEntry.status == status)
    query = query.order_by(InterestEntry.date.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=InterestEntryResponse, status_code=201)
async def create_interest_entry(
    data: InterestEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    entry = InterestEntry(
        user_id=current_user.id,
        amount=data.amount,
        source=data.source,
        date=data.date,
        description=data.description,
        status="received",
        fiscal_year=data.fiscal_year,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    await sync_fund_balance(current_user.id, db)
    return entry


@router.get("/fund-summary", response_model=InterestFundSummary)
async def get_fund_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    all_total = await db.execute(
        select(func.coalesce(func.sum(InterestEntry.amount), 0)).where(
            InterestEntry.user_id == current_user.id,
        )
    )
    total_received = float(all_total.scalar())

    distributed = await db.execute(
        select(func.coalesce(func.sum(InterestEntry.amount), 0)).where(
            InterestEntry.user_id == current_user.id,
            InterestEntry.status == "distributed",
        )
    )
    total_distributed = float(distributed.scalar())

    return InterestFundSummary(
        total_received=total_received,
        total_distributed=total_distributed,
        undistributed_balance=total_received - total_distributed,
    )


@router.get("/fiscal-year/{year}", response_model=FiscalYearSummary)
async def get_fiscal_year_summary(
    year: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    all_total = await db.execute(
        select(func.coalesce(func.sum(InterestEntry.amount), 0)).where(
            InterestEntry.user_id == current_user.id,
            InterestEntry.fiscal_year == year,
        )
    )
    total_received = float(all_total.scalar())

    distributed = await db.execute(
        select(func.coalesce(func.sum(InterestEntry.amount), 0)).where(
            InterestEntry.user_id == current_user.id,
            InterestEntry.fiscal_year == year,
            InterestEntry.status == "distributed",
        )
    )
    total_distributed = float(distributed.scalar())

    count = await db.execute(
        select(func.count(InterestEntry.id)).where(
            InterestEntry.user_id == current_user.id,
            InterestEntry.fiscal_year == year,
        )
    )
    entry_count = count.scalar()

    return FiscalYearSummary(
        fiscal_year=year,
        total_received=total_received,
        total_distributed=total_distributed,
        undistributed=total_received - total_distributed,
        entry_count=entry_count,
    )


@router.get("/{entry_id}", response_model=InterestEntryResponse)
async def get_interest_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterestEntry).where(
            InterestEntry.id == entry_id,
            InterestEntry.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Interest entry not found")
    return entry


@router.put("/{entry_id}", response_model=InterestEntryResponse)
async def update_interest_entry(
    entry_id: int,
    data: InterestEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterestEntry).where(
            InterestEntry.id == entry_id,
            InterestEntry.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Interest entry not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)

    await db.commit()
    await db.refresh(entry)
    await sync_fund_balance(current_user.id, db)
    return entry


@router.delete("/{entry_id}", status_code=204)
async def delete_interest_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterestEntry).where(
            InterestEntry.id == entry_id,
            InterestEntry.user_id == current_user.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Interest entry not found")

    await db.delete(entry)
    await db.commit()
    await sync_fund_balance(current_user.id, db)
