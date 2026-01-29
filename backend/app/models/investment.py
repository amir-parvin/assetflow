
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StockHolding(Base):
    __tablename__ = "stock_holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    ticker: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(255))
    shares: Mapped[float] = mapped_column(Numeric(15, 4))
    avg_cost: Mapped[float] = mapped_column(Numeric(15, 2))
    current_price: Mapped[float] = mapped_column(Numeric(15, 2))
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class RealEstateProperty(Base):
    __tablename__ = "real_estate_properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))
    property_type: Mapped[str] = mapped_column(String(50))
    estimated_value: Mapped[float] = mapped_column(Numeric(15, 2))
    monthly_rent: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class BusinessInterest(Base):
    __tablename__ = "business_interests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    equity_percent: Mapped[float] = mapped_column(Numeric(5, 2))
    invested_value: Mapped[float] = mapped_column(Numeric(15, 2))
    current_value: Mapped[float] = mapped_column(Numeric(15, 2))
    annual_income: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
