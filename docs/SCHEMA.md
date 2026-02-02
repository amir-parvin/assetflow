# AssetFlow - Schema Architecture

**Version:** 2.0
**Date:** 2026-01-31

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USERS                                      │
│─────────────────────────────────────────────────────────────────────│
│ PK  id              INT                                             │
│     email           VARCHAR(255)  UNIQUE                            │
│     hashed_password  VARCHAR(255)                                   │
│     full_name       VARCHAR(255)                                    │
│     currency        VARCHAR(10)   DEFAULT "USD"                     │
│     created_at      TIMESTAMPTZ                                     │
└──────────┬──────────────┬──────────────┬───────────────┬────────────┘
           │              │              │               │
           │ 1:N          │ 1:N          │ 1:N           │ 1:N
           ▼              ▼              ▼               ▼
┌──────────────────┐ ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐
│    ACCOUNTS      │ │ TRANSACTIONS│ │STOCK_HOLDINGS│ │REAL_ESTATE_      │
│──────────────────│ │─────────────│ │──────────────│ │  PROPERTIES      │
│PK id         INT │ │PK id    INT │ │PK id     INT │ │──────────────────│
│FK user_id    INT │ │FK user_id   │ │FK user_id    │ │PK id         INT │
│FK parent_id  INT │ │FK account_id│ │   ticker     │ │FK user_id    INT │
│   name       VAR │ │   amount NUM│ │   name       │ │   name       VAR │
│   type       VAR │ │   type   VAR│ │   shares NUM │ │   location   VAR │
│   category   VAR │ │   category  │ │   avg_cost   │ │   property_type  │
│   balance    NUM │ │   date  DATE│ │   current_   │ │   estimated_     │
│   currency   VAR │ │   descript. │ │     price NUM│ │     value    NUM │
│   is_active BOOL │ │   tags ARRAY│ │   sector VAR │ │   monthly_   NUM │
│   is_segment BOOL│ │   created_at│ │   created_at │ │     rent         │
│   source_type VAR│ └─────────────┘ └──────────────┘ │   created_at     │
│   source_id  INT │                                   └──────────────────┘
│   created_at     │
│   updated_at     │ ┌──────────────────┐
└──────────────────┘ │BUSINESS_INTERESTS│
        │            │──────────────────│
        │ self-ref   │PK id         INT │
        │ parent_id  │FK user_id    INT │
        ▼            │   name       VAR │
   ┌─────────┐       │   equity_pct NUM │
   │ SEGMENT │       │   invested_v NUM │
   │ (parent)│       │   current_v  NUM │
   │ Account │       │   annual_inc NUM │
   └─────────┘       │   created_at     │
                     └──────────────────┘
```

---

## The "One Purse" Hierarchy

```
USER'S PURSE (virtual - no table row)
│
├── Cash & Bank          [Segment: type=asset, category=cash, is_segment=true]
│   ├── Checking Acct    [Leaf: type=asset, category=cash, parent_id=segment]
│   ├── Savings Acct     [Leaf: type=asset, category=bank, parent_id=segment]
│   └── Emergency Fund   [Leaf: type=asset, category=cash, parent_id=segment]
│
├── Investments          [Segment: type=asset, category=investment, is_segment=true]
│   ├── AAPL - Apple     [Leaf: source_type=stock, source_id=1]
│   ├── GOOGL - Google   [Leaf: source_type=stock, source_id=2]
│   └── VOO - Vanguard   [Leaf: source_type=stock, source_id=3]
│
├── Property             [Segment: type=asset, category=property, is_segment=true]
│   ├── Primary Home     [Leaf: source_type=real_estate, source_id=1]
│   └── Rental Property  [Leaf: source_type=real_estate, source_id=2]
│
├── Business             [Segment: type=asset, category=business, is_segment=true]
│   └── Tech Startup     [Leaf: source_type=business, source_id=1]
│
└── Liabilities          [Segment: type=liability, category=liability, is_segment=true]
    ├── Home Mortgage     [Leaf: type=liability, category=mortgage]
    ├── Car Loan          [Leaf: type=liability, category=loan]
    └── Credit Card       [Leaf: type=liability, category=credit_card]
```

---

## Account Types & Categories

### Types

| Type | Description | Effect on Net Worth |
|------|-------------|---------------------|
| `asset` | Something you own | Adds to net worth |
| `liability` | Something you owe | Subtracts from net worth |
| `equity` | Reserved for future (owner's equity accounting) | - |

### Categories

| Category | Type | Description |
|----------|------|-------------|
| `cash` | asset | Physical cash, petty cash |
| `bank` | asset | Checking, savings, money market |
| `investment` | asset | Stocks, bonds, mutual funds, ETFs |
| `property` | asset | Real estate holdings |
| `vehicle` | asset | Cars, motorcycles, boats |
| `equipment` | asset | Valuable equipment, machinery |
| `crypto` | asset | Cryptocurrency holdings |
| `business` | asset | Business equity stakes |
| `mortgage` | liability | Home/property loans |
| `loan` | liability | Auto, personal, student loans |
| `credit_card` | liability | Credit card balances |
| `other` | either | Anything else |

---

## Investment-to-Account Sync

When an investment record is created or updated, a corresponding **leaf account** is automatically created/updated in the purse hierarchy:

```
StockHolding (ticker=AAPL, shares=100, current_price=150)
    │
    │  sync_investment_account()
    ▼
Account (name="AAPL - Apple Inc",
         type="asset",
         category="investment",
         balance=15000.00,          ← shares * current_price
         source_type="stock",
         source_id=<stock_holding_id>,
         parent_id=<investments_segment_id>)
    │
    │  recalculate_segment_balance()
    ▼
Investments Segment (balance = sum of all investment leaf accounts)
```

This sync ensures that:
- Portfolio values appear in the purse view
- Net worth calculations include investment values
- Balance sheet reflects current investment positions

---

## Calculation Architecture

### Current State (Broken)

```
Dashboard Endpoint ──→ SELECT * FROM accounts WHERE is_active=true
                       SUM all where type=asset    ← INCLUDES SEGMENTS (double-count!)
                       SUM all where type=liability ← INCLUDES SEGMENTS (double-count!)

Balance Sheet     ──→ Same query, same double-counting

Net Worth Report  ──→ Same query, same double-counting

Portfolio Summary ──→ Queries investment tables directly (different path, potentially different total)
```

### Target State (Fixed)

```
                    ┌─────────────────────────┐
                    │   CalculationService     │
                    │─────────────────────────│
                    │ get_total_assets()       │  ← WHERE is_segment=false
                    │ get_total_liabilities()  │  ← WHERE is_segment=false
                    │ get_net_worth()          │
                    │ get_monthly_income()     │
                    │ get_monthly_expense()    │
                    │ get_savings_rate()       │
                    │ get_debt_to_asset_ratio()│
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                   │
              ▼                  ▼                   ▼
    Dashboard Endpoint   Balance Sheet       Net Worth Report
    (consistent)         (consistent)        (consistent)
```

### Key Rule

> **NEVER sum accounts where `is_segment=true`.** Segment balances are derived values (sum of children). Including them in totals double-counts every dollar.

---

## Transaction Flow

```
User creates transaction (type=expense, amount=50, account_id=checking)
    │
    ├──→ Transaction record created
    │
    └──→ Account balance updated?  ← NOTE: Currently transactions do NOT
                                      auto-update account balances.
                                      Balances are manually set.
                                      This is a known limitation.
```

---

## Data Flow: Dashboard API

```
GET /reports/dashboard
    │
    ├──→ Query leaf accounts (is_segment=false, is_active=true)
    │    ├── SUM assets → total_assets
    │    └── SUM liabilities → total_liabilities
    │
    ├──→ net_worth = total_assets - total_liabilities
    │
    ├──→ Query transactions (last 30 days)
    │    ├── SUM income → monthly_income
    │    └── SUM expense → monthly_expense
    │
    ├──→ savings_rate = (income - expense) / income * 100
    │
    ├──→ Query last 5 transactions → recent_transactions
    │
    ├──→ Group leaf asset accounts by category → asset_allocation
    │
    └──→ Group leaf liability accounts by category → liability_allocation
```

---

## Database Indexes

| Table | Column(s) | Purpose |
|-------|-----------|---------|
| accounts | user_id | User isolation |
| accounts | parent_id | Segment hierarchy lookups |
| transactions | user_id | User isolation |
| transactions | account_id | Account-scoped queries |
| transactions | date | Date range filtering |
| stock_holdings | user_id | User isolation |
| real_estate_properties | user_id | User isolation |
| business_interests | user_id | User isolation |
