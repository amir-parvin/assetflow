from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.account import Account
from app.models.investment import StockHolding, RealEstateProperty, BusinessInterest
from app.models.user import User
from app.schemas.zakat import ZakatRequest, ZakatResponse, ZakatBreakdown

router = APIRouter(prefix="/zakat", tags=["zakat"])

GOLD_NISAB_GRAMS = 87.48
SILVER_NISAB_GRAMS = 612.36


@router.post("/calculate", response_model=ZakatResponse)
async def calculate_zakat(
    data: ZakatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Cash & bank accounts (exclude segments to avoid double-counting)
    accts = await db.execute(
        select(Account).where(
            Account.user_id == current_user.id,
            Account.is_active == True,
            Account.is_segment == False,
            Account.type == "asset",
            Account.category.in_(["cash", "bank"]),
        )
    )
    cash_and_bank = sum(float(a.balance) for a in accts.scalars().all())

    # Investments (stocks)
    stocks = await db.execute(select(StockHolding).where(StockHolding.user_id == current_user.id))
    investments = sum(float(s.shares) * float(s.current_price) for s in stocks.scalars().all())

    # Real estate rental income (annual)
    props = await db.execute(select(RealEstateProperty).where(RealEstateProperty.user_id == current_user.id))
    re_income = sum(float(p.monthly_rent) * 12 for p in props.scalars().all())

    # Business interests
    biz = await db.execute(select(BusinessInterest).where(BusinessInterest.user_id == current_user.id))
    biz_value = sum(float(b.current_value) for b in biz.scalars().all())

    total_zakatable = cash_and_bank + investments + re_income + biz_value

    if data.use_gold_nisab:
        nisab = GOLD_NISAB_GRAMS * data.gold_price_per_gram
    else:
        nisab = SILVER_NISAB_GRAMS * data.silver_price_per_gram

    is_above = total_zakatable >= nisab
    zakat_due = total_zakatable * 0.025 if is_above else 0

    return ZakatResponse(
        breakdown=ZakatBreakdown(
            cash_and_bank=cash_and_bank,
            investments=investments,
            real_estate_rent_income=re_income,
            business_interests=biz_value,
            total_zakatable=total_zakatable,
            nisab_threshold=nisab,
            is_above_nisab=is_above,
            zakat_due=round(zakat_due, 2),
        ),
        rate=0.025,
    )
