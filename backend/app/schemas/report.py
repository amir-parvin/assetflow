from pydantic import BaseModel


class NetWorthPoint(BaseModel):
    date: str
    assets: float
    liabilities: float
    net_worth: float


class NetWorthReport(BaseModel):
    current_net_worth: float
    history: list[NetWorthPoint]


class BalanceSheetItem(BaseModel):
    category: str
    total: float
    accounts: list[dict]


class BalanceSheetReport(BaseModel):
    total_assets: float
    total_liabilities: float
    net_worth: float
    assets: list[BalanceSheetItem]
    liabilities: list[BalanceSheetItem]


class IncomeExpenseReport(BaseModel):
    period: str
    total_income: float
    total_expense: float
    net: float
    by_category: list[dict]


class CashFlowPoint(BaseModel):
    period: str
    inflow: float
    outflow: float
    net: float


class CashFlowReport(BaseModel):
    data: list[CashFlowPoint]


class DashboardSummary(BaseModel):
    net_worth: float
    total_assets: float
    total_liabilities: float
    monthly_income: float
    monthly_expense: float
    savings_rate: float = 0.0
    debt_to_asset_ratio: float = 0.0
    recent_transactions: list[dict]
    asset_allocation: list[dict]
    liability_allocation: list[dict] = []
