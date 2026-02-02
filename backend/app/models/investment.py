
from datetime import date, datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Text, Date
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
    cost_basis: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    area_size: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    roi_percent: Mapped[float | None] = mapped_column(Numeric(7, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class GoldHolding(Base):
    __tablename__ = "gold_holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    gold_type: Mapped[str] = mapped_column(String(50))  # bar, coin, jewelry, etf
    weight_grams: Mapped[float] = mapped_column(Numeric(12, 4))
    purity: Mapped[float] = mapped_column(Numeric(5, 2), default=99.9)
    purchase_price: Mapped[float] = mapped_column(Numeric(15, 2))
    current_value: Mapped[float] = mapped_column(Numeric(15, 2))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    vehicle_type: Mapped[str] = mapped_column(String(50))  # car, motorcycle, boat, etc.
    make: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    year: Mapped[int | None] = mapped_column(nullable=True)
    purchase_price: Mapped[float] = mapped_column(Numeric(15, 2))
    current_value: Mapped[float] = mapped_column(Numeric(15, 2))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class InterestEntry(Base):
    __tablename__ = "interest_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    rate: Mapped[float | None] = mapped_column(Numeric(7, 4), nullable=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class NetWorthSnapshot(Base):
    __tablename__ = "net_worth_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    total_assets: Mapped[float] = mapped_column(Numeric(15, 2))
    total_liabilities: Mapped[float] = mapped_column(Numeric(15, 2))
    net_worth: Mapped[float] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    breakdown: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string of per-segment totals
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class GoldHolding(Base):
    __tablename__ = "gold_holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    weight_vori: Mapped[float] = mapped_column(Numeric(15, 4))
    purchase_price_per_vori: Mapped[float] = mapped_column(Numeric(15, 2))
    current_price_per_vori: Mapped[float] = mapped_column(Numeric(15, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
