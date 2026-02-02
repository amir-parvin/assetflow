from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.investment import GoldHolding
from app.models.user import User
from app.schemas.investment import (
    GoldHoldingCreate, GoldHoldingUpdate, GoldHoldingResponse, GRAMS_PER_VORI,
)
from app.api.investments import sync_investment_account, remove_investment_account

router = APIRouter(prefix="/investments/gold", tags=["gold"])


def _build_response(h: GoldHolding) -> GoldHoldingResponse:
    w = float(h.weight_vori)
    cp = float(h.current_price_per_vori)
    pp = float(h.purchase_price_per_vori)
    cv = w * cp
    cost = w * pp
    resp = GoldHoldingResponse.model_validate(h)
    resp.weight_grams = round(w * GRAMS_PER_VORI, 4)
    resp.current_value = cv
    resp.gain_loss = cv - cost
    return resp


@router.get("", response_model=list[GoldHoldingResponse])
async def list_gold(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GoldHolding).where(GoldHolding.user_id == current_user.id))
    return [_build_response(h) for h in result.scalars().all()]


@router.post("", response_model=GoldHoldingResponse, status_code=201)
async def create_gold(
    data: GoldHoldingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    weight_vori = data.weight_in_vori()
    holding = GoldHolding(
        user_id=current_user.id,
        name=data.name,
        weight_vori=weight_vori,
        purchase_price_per_vori=data.purchase_price_per_vori,
        current_price_per_vori=data.current_price_per_vori,
    )
    db.add(holding)
    await db.commit()
    await db.refresh(holding)

    cv = weight_vori * data.current_price_per_vori
    await sync_investment_account(
        current_user.id, "gold", holding.id, holding.name, cv, "gold", db
    )

    return _build_response(holding)


@router.put("/{gold_id}", response_model=GoldHoldingResponse)
async def update_gold(
    gold_id: int,
    data: GoldHoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GoldHolding).where(GoldHolding.id == gold_id, GoldHolding.user_id == current_user.id)
    )
    holding = result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="Gold holding not found")

    new_vori = data.weight_in_vori(float(holding.weight_vori))
    holding.weight_vori = new_vori
    if data.purchase_price_per_vori is not None:
        holding.purchase_price_per_vori = data.purchase_price_per_vori
    if data.current_price_per_vori is not None:
        holding.current_price_per_vori = data.current_price_per_vori
    if data.name is not None:
        holding.name = data.name
    await db.commit()
    await db.refresh(holding)

    cv = float(holding.weight_vori) * float(holding.current_price_per_vori)
    await sync_investment_account(
        current_user.id, "gold", holding.id, holding.name, cv, "gold", db
    )

    return _build_response(holding)


@router.delete("/{gold_id}", status_code=204)
async def delete_gold(
    gold_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GoldHolding).where(GoldHolding.id == gold_id, GoldHolding.user_id == current_user.id)
    )
    holding = result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="Gold holding not found")
    await remove_investment_account(current_user.id, "gold", holding.id, db)
    await db.delete(holding)
    await db.commit()
