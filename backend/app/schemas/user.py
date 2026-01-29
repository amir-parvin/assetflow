from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    currency: str = "USD"


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    currency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    full_name: str | None = None
    currency: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str
