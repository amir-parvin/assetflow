"""T1 schema migration - new fields and tables

Revision ID: 001_t1_schema
Revises:
Create Date: 2026-02-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_t1_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Create all base tables first ---

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("currency", sa.String(10), server_default="USD", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("accounts.id"), index=True, nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("balance", sa.Numeric(15, 2), server_default="0", nullable=False),
        sa.Column("currency", sa.String(10), server_default="USD", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_segment", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("sub_category", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id"), index=True, nullable=False),
        sa.Column("to_account_id", sa.Integer(), sa.ForeignKey("accounts.id"), index=True, nullable=True),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("date", sa.Date(), index=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "stock_holdings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("shares", sa.Numeric(15, 4), nullable=False),
        sa.Column("avg_cost", sa.Numeric(15, 2), nullable=False),
        sa.Column("current_price", sa.Numeric(15, 2), nullable=False),
        sa.Column("sector", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "real_estate_properties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("property_type", sa.String(50), nullable=False),
        sa.Column("estimated_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("monthly_rent", sa.Numeric(15, 2), server_default="0", nullable=False),
        sa.Column("cost_basis", sa.Numeric(15, 2), nullable=True),
        sa.Column("area_size", sa.Numeric(12, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "business_interests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("equity_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("invested_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("current_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("annual_income", sa.Numeric(15, 2), server_default="0", nullable=False),
        sa.Column("roi_percent", sa.Numeric(7, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "gold_holdings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("gold_type", sa.String(50), nullable=False),
        sa.Column("weight_grams", sa.Numeric(12, 4), nullable=False),
        sa.Column("purity", sa.Numeric(5, 2), server_default="99.9", nullable=False),
        sa.Column("purchase_price", sa.Numeric(15, 2), nullable=False),
        sa.Column("current_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("vehicle_type", sa.String(50), nullable=False),
        sa.Column("make", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("purchase_price", sa.Numeric(15, 2), nullable=False),
        sa.Column("current_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "interest_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id"), index=True, nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("rate", sa.Numeric(7, 4), nullable=True),
        sa.Column("date", sa.Date(), index=True, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "net_worth_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("date", sa.Date(), index=True, nullable=False),
        sa.Column("total_assets", sa.Numeric(15, 2), nullable=False),
        sa.Column("total_liabilities", sa.Numeric(15, 2), nullable=False),
        sa.Column("net_worth", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(10), server_default="USD", nullable=False),
        sa.Column("breakdown", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("net_worth_snapshots")
    op.drop_table("interest_entries")
    op.drop_table("vehicles")
    op.drop_table("gold_holdings")
    op.drop_table("business_interests")
    op.drop_table("real_estate_properties")
    op.drop_table("stock_holdings")
    op.drop_table("transactions")
    op.drop_table("accounts")
    op.drop_table("users")
