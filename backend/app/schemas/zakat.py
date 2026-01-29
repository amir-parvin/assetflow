from pydantic import BaseModel


class ZakatRequest(BaseModel):
    gold_price_per_gram: float = 75.0  # USD
    silver_price_per_gram: float = 0.90  # USD
    use_gold_nisab: bool = True  # Gold nisab = 87.48g, Silver nisab = 612.36g


class ZakatBreakdown(BaseModel):
    cash_and_bank: float
    investments: float
    real_estate_rent_income: float
    business_interests: float
    total_zakatable: float
    nisab_threshold: float
    is_above_nisab: bool
    zakat_due: float  # 2.5% of zakatable if above nisab


class ZakatResponse(BaseModel):
    breakdown: ZakatBreakdown
    rate: float = 0.025
