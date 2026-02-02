import datetime as dt
from pydantic import BaseModel


class InterestEntryCreate(BaseModel):
    amount: float
    source: str
    date: dt.datetime
    description: str | None = None
    fiscal_year: int


class InterestEntryUpdate(BaseModel):
    amount: float | None = None
    source: str | None = None
    date: dt.datetime | None = None
    description: str | None = None
    status: str | None = None
    fiscal_year: int | None = None


class InterestEntryResponse(BaseModel):
    id: int
    amount: float
    source: str
    date: dt.datetime
    description: str | None
    status: str
    fiscal_year: int
    created_at: dt.datetime

    model_config = {"from_attributes": True}


class InterestFundSummary(BaseModel):
    total_received: float
    total_distributed: float
    undistributed_balance: float


class FiscalYearSummary(BaseModel):
    fiscal_year: int
    total_received: float
    total_distributed: float
    undistributed: float
    entry_count: int
