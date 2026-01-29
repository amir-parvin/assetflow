from datetime import datetime
from pydantic import BaseModel


class AccountCreate(BaseModel):
    name: str
    type: str  # asset, liability, equity
    category: str
    balance: float = 0
    currency: str = "USD"
    parent_id: int | None = None


class AccountUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    category: str | None = None
    balance: float | None = None
    currency: str | None = None
    is_active: bool | None = None
    parent_id: int | None = None


class AccountResponse(BaseModel):
    id: int
    user_id: int
    parent_id: int | None
    name: str
    type: str
    category: str
    balance: float
    currency: str
    is_active: bool
    is_segment: bool
    source_type: str | None
    source_id: int | None
    created_at: datetime
    updated_at: datetime
    children: list["AccountResponse"] = []

    model_config = {"from_attributes": True}


class SegmentSummary(BaseModel):
    id: int
    name: str
    category: str
    total_balance: float
    currency: str
    sub_segments: list[AccountResponse]
