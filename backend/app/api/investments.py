from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.account import Account
from app.models.investment import StockHolding, RealEstateProperty, BusinessInterest, GoldHolding
from app.models.user import User
from app.schemas.investment import (
    StockHoldingCreate, StockHoldingUpdate, StockHoldingResponse,
    RealEstateCreate, RealEstateUpdate, RealEstateResponse,
    BusinessInterestCreate, BusinessInterestUpdate, BusinessInterestResponse,
    PortfolioSummary,
)
from app.api.accounts import get_or_create_segment, recalculate_segment_balance

router = APIRouter(prefix="/investments", tags=["investments"])


async def sync_investment_account(
    user_id: int, source_type: str, source_id: int,
    name: str, value: float, category: str, db: AsyncSession,
):
    result = await db.execute(
        select(Account).where(
            Account.user_id == user_id,
            Account.source_type == source_type,
            Account.source_id == source_id,
        )
    )
    acct = result.scalar_one_or_none()
    segment = await get_or_create_segment(user_id, category, db)

    if acct:
        acct.name = name
        acct.balance = value
    else:
        acct = Account(
            user_id=user_id,
            parent_id=segment.id,
            name=name,
            type="asset",
            category=category,
            balance=value,
            source_type=source_type,
            source_id=source_id,
        )
        db.add(acct)
    await db.commit()
    await recalculate_segment_balance(segment.id, db)


async def remove_investment_account(user_id: int, source_type: str, source_id: int, db: AsyncSession):
    result = await db.execute(
        select(Account).where(
            Account.user_id == user_id,
            Account.source_type == source_type,
            Account.source_id == source_id,
        )
    )
    acct = result.scalar_one_or_none()
    if acct:
        parent_id = acct.parent_id
        await db.delete(acct)
        await db.commit()
        if parent_id:
            await recalculate_segment_balance(parent_id, db)


# --- Stocks ---

@router.get("/stocks", response_model=list[StockHoldingResponse])
async def list_stocks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(StockHolding).where(StockHolding.user_id == current_user.id))
    out = []
    for h in result.scalars().all():
        mv = float(h.shares) * float(h.current_price)
        cost = float(h.shares) * float(h.avg_cost)
        gl = mv - cost
        gl_pct = (gl / cost * 100) if cost else 0
        resp = StockHoldingResponse.model_validate(h)
        resp.market_value = mv
        resp.gain_loss = gl
        resp.gain_loss_pct = round(gl_pct, 2)
        out.append(resp)
    return out


@router.post("/stocks", response_model=StockHoldingResponse, status_code=201)
async def create_stock(
    data: StockHoldingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stock = StockHolding(user_id=current_user.id, **data.model_dump())
    db.add(stock)
    await db.commit()
    await db.refresh(stock)

    mv = float(stock.shares) * float(stock.current_price)
    cost = float(stock.shares) * float(stock.avg_cost)
    await sync_investment_account(
        current_user.id, "stock", stock.id, f"{stock.ticker} - {stock.name}", mv, "investment", db
    )

    resp = StockHoldingResponse.model_validate(stock)
    resp.market_value = mv
    resp.gain_loss = mv - cost
    resp.gain_loss_pct = round((mv - cost) / cost * 100, 2) if cost else 0
    return resp


@router.put("/stocks/{stock_id}", response_model=StockHoldingResponse)
async def update_stock(
    stock_id: int,
    data: StockHoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StockHolding).where(StockHolding.id == stock_id, StockHolding.user_id == current_user.id)
    )
    stock = result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(stock, k, v)
    await db.commit()
    await db.refresh(stock)

    mv = float(stock.shares) * float(stock.current_price)
    cost = float(stock.shares) * float(stock.avg_cost)
    await sync_investment_account(
        current_user.id, "stock", stock.id, f"{stock.ticker} - {stock.name}", mv, "investment", db
    )

    resp = StockHoldingResponse.model_validate(stock)
    resp.market_value = mv
    resp.gain_loss = mv - cost
    resp.gain_loss_pct = round((mv - cost) / cost * 100, 2) if cost else 0
    return resp


@router.delete("/stocks/{stock_id}", status_code=204)
async def delete_stock(
    stock_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StockHolding).where(StockHolding.id == stock_id, StockHolding.user_id == current_user.id)
    )
    stock = result.scalar_one_or_none()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    await remove_investment_account(current_user.id, "stock", stock.id, db)
    await db.delete(stock)
    await db.commit()


# --- Real Estate ---

@router.get("/real-estate", response_model=list[RealEstateResponse])
async def list_real_estate(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(RealEstateProperty).where(RealEstateProperty.user_id == current_user.id))
    out = []
    for p in result.scalars().all():
        resp = RealEstateResponse.model_validate(p)
        resp.annual_rent = float(p.monthly_rent) * 12
        out.append(resp)
    return out


@router.post("/real-estate", response_model=RealEstateResponse, status_code=201)
async def create_real_estate(
    data: RealEstateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    prop = RealEstateProperty(user_id=current_user.id, **data.model_dump())
    db.add(prop)
    await db.commit()
    await db.refresh(prop)

    await sync_investment_account(
        current_user.id, "real_estate", prop.id, prop.name, float(prop.estimated_value), "property", db
    )

    resp = RealEstateResponse.model_validate(prop)
    resp.annual_rent = float(prop.monthly_rent) * 12
    return resp


@router.put("/real-estate/{prop_id}", response_model=RealEstateResponse)
async def update_real_estate(
    prop_id: int,
    data: RealEstateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RealEstateProperty).where(RealEstateProperty.id == prop_id, RealEstateProperty.user_id == current_user.id)
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(prop, k, v)
    await db.commit()
    await db.refresh(prop)

    await sync_investment_account(
        current_user.id, "real_estate", prop.id, prop.name, float(prop.estimated_value), "property", db
    )

    resp = RealEstateResponse.model_validate(prop)
    resp.annual_rent = float(prop.monthly_rent) * 12
    return resp


@router.delete("/real-estate/{prop_id}", status_code=204)
async def delete_real_estate(
    prop_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RealEstateProperty).where(RealEstateProperty.id == prop_id, RealEstateProperty.user_id == current_user.id)
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    await remove_investment_account(current_user.id, "real_estate", prop.id, db)
    await db.delete(prop)
    await db.commit()


# --- Business Interests ---

@router.get("/business", response_model=list[BusinessInterestResponse])
async def list_business(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(BusinessInterest).where(BusinessInterest.user_id == current_user.id))
    out = []
    for b in result.scalars().all():
        resp = BusinessInterestResponse.model_validate(b)
        resp.gain_loss = float(b.current_value) - float(b.invested_value)
        out.append(resp)
    return out


@router.post("/business", response_model=BusinessInterestResponse, status_code=201)
async def create_business(
    data: BusinessInterestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    biz = BusinessInterest(user_id=current_user.id, **data.model_dump())
    db.add(biz)
    await db.commit()
    await db.refresh(biz)

    await sync_investment_account(
        current_user.id, "business", biz.id, biz.name, float(biz.current_value), "business", db
    )

    resp = BusinessInterestResponse.model_validate(biz)
    resp.gain_loss = float(biz.current_value) - float(biz.invested_value)
    return resp


@router.put("/business/{biz_id}", response_model=BusinessInterestResponse)
async def update_business(
    biz_id: int,
    data: BusinessInterestUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BusinessInterest).where(BusinessInterest.id == biz_id, BusinessInterest.user_id == current_user.id)
    )
    biz = result.scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business interest not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(biz, k, v)
    await db.commit()
    await db.refresh(biz)

    await sync_investment_account(
        current_user.id, "business", biz.id, biz.name, float(biz.current_value), "business", db
    )

    resp = BusinessInterestResponse.model_validate(biz)
    resp.gain_loss = float(biz.current_value) - float(biz.invested_value)
    return resp


@router.delete("/business/{biz_id}", status_code=204)
async def delete_business(
    biz_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BusinessInterest).where(BusinessInterest.id == biz_id, BusinessInterest.user_id == current_user.id)
    )
    biz = result.scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business interest not found")
    await remove_investment_account(current_user.id, "business", biz.id, db)
    await db.delete(biz)
    await db.commit()


# --- Portfolio Summary ---

@router.get("/portfolio", response_model=PortfolioSummary)
async def portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stocks = await db.execute(select(StockHolding).where(StockHolding.user_id == current_user.id))
    all_stocks = stocks.scalars().all()
    total_stocks = sum(float(s.shares) * float(s.current_price) for s in all_stocks)
    stocks_cost = sum(float(s.shares) * float(s.avg_cost) for s in all_stocks)

    props = await db.execute(select(RealEstateProperty).where(RealEstateProperty.user_id == current_user.id))
    total_re = sum(float(p.estimated_value) for p in props.scalars().all())

    biz = await db.execute(select(BusinessInterest).where(BusinessInterest.user_id == current_user.id))
    all_biz = biz.scalars().all()
    total_biz = sum(float(b.current_value) for b in all_biz)
    biz_cost = sum(float(b.invested_value) for b in all_biz)

    golds = await db.execute(select(GoldHolding).where(GoldHolding.user_id == current_user.id))
    all_gold = golds.scalars().all()
    total_gold = sum(float(g.weight_vori) * float(g.current_price_per_vori) for g in all_gold)
    gold_cost = sum(float(g.weight_vori) * float(g.purchase_price_per_vori) for g in all_gold)

    total = total_stocks + total_re + total_biz + total_gold
    total_gl = (total_stocks - stocks_cost) + (total_biz - biz_cost) + (total_gold - gold_cost)

    return PortfolioSummary(
        total_stocks_value=total_stocks,
        total_real_estate_value=total_re,
        total_business_value=total_biz,
        total_gold_value=total_gold,
        total_portfolio_value=total,
        total_gain_loss=total_gl,
    )
