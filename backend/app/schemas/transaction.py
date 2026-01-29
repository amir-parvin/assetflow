import datetime as dt
from pydantic import BaseModel


class TransactionCreate(BaseModel):
    account_id: int
    amount: float
    type: str  # income, expense, transfer
    category: str
    date: dt.date
    description: str | None = None
    tags: list[str] | None = None


class TransactionUpdate(BaseModel):
    account_id: int | None = None
    amount: float | None = None
    type: str | None = None
    category: str | None = None
    date: dt.date | None = None
    description: str | None = None
    tags: list[str] | None = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    amount: float
    type: str
    category: str
    date: dt.date
    description: str | None
    tags: list[str] | None
    created_at: dt.datetime

    model_config = {"from_attributes": True}


class TransactionFilter(BaseModel):
    account_id: int | None = None
    type: str | None = None
    category: str | None = None
    date_from: dt.date | None = None
    date_to: dt.date | None = None
    page: int = 1
    per_page: int = 20
