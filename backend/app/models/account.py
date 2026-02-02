from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(50))  # asset, liability, equity
    category: Mapped[str] = mapped_column(String(50))  # cash, bank, investment, property, vehicle, equipment, crypto, loan, credit_card, mortgage, other
    balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_segment: Mapped[bool] = mapped_column(Boolean, default=False)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # stock, real_estate, business
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sub_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    children: Mapped[list["Account"]] = relationship("Account", back_populates="parent", lazy="selectin")
    parent: Mapped["Account | None"] = relationship("Account", back_populates="children", remote_side=[id], lazy="selectin")
