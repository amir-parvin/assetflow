from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse, SegmentSummary

router = APIRouter(prefix="/accounts", tags=["accounts"])


DEFAULT_SEGMENTS = [
    {"name": "Cash & Bank", "type": "asset", "category": "cash"},
    {"name": "Investments", "type": "asset", "category": "investment"},
    {"name": "Property", "type": "asset", "category": "property"},
    {"name": "Business", "type": "asset", "category": "business"},
    {"name": "Gold", "type": "asset", "category": "gold"},
    {"name": "Vehicles", "type": "asset", "category": "vehicle"},
    {"name": "Other Assets", "type": "asset", "category": "other"},
    {"name": "Liabilities", "type": "liability", "category": "liability"},
]


async def ensure_segments(user_id: int, db: AsyncSession) -> list[Account]:
    result = await db.execute(
        select(Account).where(Account.user_id == user_id, Account.is_segment == True, Account.parent_id == None)
    )
    segments = list(result.scalars().all())
    if segments:
        return segments

    for seg in DEFAULT_SEGMENTS:
        account = Account(user_id=user_id, is_segment=True, balance=0, **seg)
        db.add(account)
        segments.append(account)
    await db.commit()
    for s in segments:
        await db.refresh(s)
    return segments


async def get_or_create_segment(user_id: int, category: str, db: AsyncSession) -> Account:
    result = await db.execute(
        select(Account).where(
            Account.user_id == user_id, Account.is_segment == True,
            Account.parent_id == None, Account.category == category,
        )
    )
    seg = result.scalar_one_or_none()
    if seg:
        return seg
    segments = await ensure_segments(user_id, db)
    for s in segments:
        if s.category == category:
            return s
    seg_info = next((s for s in DEFAULT_SEGMENTS if s["category"] == category), DEFAULT_SEGMENTS[0])
    seg = Account(user_id=user_id, is_segment=True, balance=0, **seg_info)
    db.add(seg)
    await db.commit()
    await db.refresh(seg)
    return seg


async def recalculate_segment_balance(segment_id: int, db: AsyncSession):
    result = await db.execute(
        select(Account).where(Account.parent_id == segment_id, Account.is_active == True)
    )
    children = result.scalars().all()
    total = sum(float(c.balance) for c in children)
    seg_result = await db.execute(select(Account).where(Account.id == segment_id))
    seg = seg_result.scalar_one_or_none()
    if seg:
        seg.balance = total
        await db.commit()


@router.get("/purse", response_model=list[SegmentSummary])
async def get_purse(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    segments = await ensure_segments(current_user.id, db)
    result = []
    for seg in segments:
        children_result = await db.execute(
            select(Account).where(Account.parent_id == seg.id, Account.is_active == True)
            .options(selectinload(Account.children))
            .order_by(Account.created_at.desc())
        )
        children = list(children_result.scalars().all())
        total = sum(float(c.balance) for c in children)
        result.append(SegmentSummary(
            id=seg.id,
            name=seg.name,
            category=seg.category,
            total_balance=total,
            currency=current_user.currency,
            sub_segments=[AccountResponse.model_validate(c) for c in children],
        ))
    return result


@router.get("", response_model=list[AccountResponse])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Account).where(Account.user_id == current_user.id)
        .options(selectinload(Account.children))
        .order_by(Account.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=AccountResponse, status_code=201)
async def create_account(
    data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    parent_id = data.parent_id
    if not parent_id:
        segment = await get_or_create_segment(current_user.id, data.category, db)
        parent_id = segment.id

    account = Account(
        user_id=current_user.id,
        parent_id=parent_id,
        name=data.name,
        type=data.type,
        category=data.category,
        balance=data.balance,
        currency=data.currency or current_user.currency,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    await recalculate_segment_balance(parent_id, db)
    return account


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(account, key, value)

    await db.commit()
    await db.refresh(account)
    if account.parent_id:
        await recalculate_segment_balance(account.parent_id, db)
    return account


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    parent_id = account.parent_id
    await db.delete(account)
    await db.commit()
    if parent_id:
        await recalculate_segment_balance(parent_id, db)
