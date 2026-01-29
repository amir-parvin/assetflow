
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


class PortfolioSummary(BaseModel):
    total_stocks_value: float
    total_real_estate_value: float
    total_business_value: float
    total_portfolio_value: float
    total_gain_loss: float
