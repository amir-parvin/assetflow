
from datetime import datetime
from pydantic import BaseModel


class StockHoldingCreate(BaseModel):
    ticker: str
    name: str
    shares: float
    avg_cost: float
    current_price: float
    sector: str | None = None


class StockHoldingUpdate(BaseModel):
    ticker: str | None = None
    name: str | None = None
    shares: float | None = None
    avg_cost: float | None = None
    current_price: float | None = None
    sector: str | None = None


class StockHoldingResponse(BaseModel):
    id: int
    user_id: int
    ticker: str
    name: str
    shares: float
    avg_cost: float
    current_price: float
    sector: str | None
    market_value: float = 0
    gain_loss: float = 0
    gain_loss_pct: float = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class RealEstateCreate(BaseModel):
    name: str
    location: str
    property_type: str
    estimated_value: float
    monthly_rent: float = 0


class RealEstateUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    property_type: str | None = None
    estimated_value: float | None = None
    monthly_rent: float | None = None


class RealEstateResponse(BaseModel):
    id: int
    user_id: int
    name: str
    location: str
    property_type: str
    estimated_value: float
    monthly_rent: float
    annual_rent: float = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class BusinessInterestCreate(BaseModel):
    name: str
    equity_percent: float
    invested_value: float
    current_value: float
    annual_income: float = 0


class BusinessInterestUpdate(BaseModel):
    name: str | None = None
    equity_percent: float | None = None
    invested_value: float | None = None
    current_value: float | None = None
    annual_income: float | None = None


class BusinessInterestResponse(BaseModel):
    id: int
    user_id: int
    name: str
    equity_percent: float
    invested_value: float
    current_value: float
    annual_income: float
    gain_loss: float = 0
    created_at: datetime

    model_config = {"from_attributes": True}


GRAMS_PER_VORI = 11.664


class GoldHoldingCreate(BaseModel):
    name: str
    weight: float
    weight_unit: str = "vori"  # "vori" or "gram"
    purchase_price_per_vori: float
    current_price_per_vori: float

    def weight_in_vori(self) -> float:
        if self.weight_unit == "gram":
            return self.weight / GRAMS_PER_VORI
        return self.weight


class GoldHoldingUpdate(BaseModel):
    name: str | None = None
    weight: float | None = None
    weight_unit: str | None = None  # "vori" or "gram"
    purchase_price_per_vori: float | None = None
    current_price_per_vori: float | None = None

    def weight_in_vori(self, current_vori: float) -> float:
        if self.weight is not None:
            unit = self.weight_unit or "vori"
            if unit == "gram":
                return self.weight / GRAMS_PER_VORI
            return self.weight
        return current_vori


class GoldHoldingResponse(BaseModel):
    id: int
    user_id: int
    name: str
    weight_vori: float
    weight_grams: float = 0
    purchase_price_per_vori: float
    current_price_per_vori: float
    current_value: float = 0
    gain_loss: float = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class PortfolioSummary(BaseModel):
    total_stocks_value: float
    total_real_estate_value: float
    total_business_value: float
    total_gold_value: float = 0
    total_portfolio_value: float
    total_gain_loss: float
