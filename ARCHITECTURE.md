# AssetFlow - Architecture

## Core Design Philosophy

**"Edit-first, not Transaction-first"**

Your spreadsheet workflow: open cell → change value → done.
AssetFlow works the same way. Transactions exist for cash-flow tracking (income/expenses),
but asset values (land, gold, stocks) are updated by **directly editing the balance** — just like Excel.

**Interests Isolation (Islamic Finance)**
Interest money is haram to use personally. It must be tracked separately and distributed to charity.
This is a first-class accounting concern with its own fund, ledger, and distribution tracking.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ASSETFLOW SYSTEM                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────┐         ┌──────────────────────────────┐ │
│  │   FRONTEND (Next.js) │  HTTP   │    BACKEND (FastAPI)         │ │
│  │   Port 3000          │────────>│    Port 8000                 │ │
│  │                      │<────────│                              │ │
│  │  ┌────────────────┐  │  JSON   │  ┌────────────────────────┐ │ │
│  │  │ Pages          │  │         │  │ API Routes             │ │ │
│  │  │  Dashboard     │  │         │  │  /auth/*               │ │ │
│  │  │  Purse         │  │         │  │  /accounts/*           │ │ │
│  │  │  Liabilities   │  │         │  │  /transactions/*       │ │ │
│  │  │  Transactions  │  │         │  │  /investments/*        │ │ │
│  │  │  Investments   │  │         │  │  /reports/*            │ │ │
│  │  │  Income/Expense│  │         │  │  /zakat/*              │ │ │
│  │  │  Reports       │  │         │  │  /interests/*          │ │ │
│  │  │  Zakat         │  │         │  └───────────┬────────────┘ │ │
│  │  │  Settings      │  │         │               │              │ │
│  │  └────────────────┘  │         │  ┌────────────▼────────────┐ │ │
│  │                      │         │  │ PostgreSQL 15           │ │ │
│  │  ┌────────────────┐  │         │  │  users                  │ │ │
│  │  │ Hooks/Context  │  │         │  │  accounts               │ │ │
│  │  │  useAuth       │  │         │  │  transactions           │ │ │
│  │  │  useToast      │  │         │  │  stock_holdings         │ │ │
│  │  └────────────────┘  │         │  │  real_estate_properties │ │ │
│  │                      │         │  │  business_interests     │ │ │
│  │  ┌────────────────┐  │         │  │  gold_holdings          │ │ │
│  │  │ lib/api.ts     │  │         │  │  vehicles               │ │ │
│  │  │ lib/utils.ts   │  │         │  │  net_worth_snapshots    │ │ │
│  │  └────────────────┘  │         │  │  interest_entries       │ │ │
│  │                      │         │  └─────────────────────────┘ │ │
│  │  ┌────────────────┐  │         │                              │ │
│  │  │ UI Components  │  │         │  Design: No rounded corners  │ │
│  │  │ Charts         │  │         │  Grayscale + Gold (#E5C07B)  │ │
│  │  └────────────────┘  │         │  Inter + JetBrains Mono      │ │
│  └──────────────────────┘         └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Database Schema

```
┌──────────────────────┐
│       USERS          │
├──────────────────────┤
│ PK id                │
│    email (unique)    │
│    hashed_password   │
│    full_name         │
│    currency (BDT)    │
│    created_at        │
└──────────┬───────────┘
           │ 1:N
           ▼
┌─────────────────────────────┐      self-ref
│       ACCOUNTS              │◄────────────┐
├─────────────────────────────┤             │
│ PK id                       │             │
│ FK user_id ──► users        │             │
│ FK parent_id ──► accounts   ├─────────────┘
│    name                     │
│    type (asset/liability)   │
│    category                 │  cash/bank/investment/property/
│                             │  vehicle/gold/equipment/crypto/
│                             │  loan/credit_card/mortgage/
│                             │  business/livestock/other/liability
│    sub_category             │  checking/savings/fdr/dps/
│                             │  lent/borrowed/fund/receivable
│    balance (15,2)           │  ◄── DIRECTLY EDITABLE
│    currency                 │
│    is_active                │
│    is_segment               │
│    source_type              │  stock/real_estate/business/gold/vehicle
│    source_id                │
│    notes                    │  ◄── Bengali annotations
│    created_at, updated_at   │
└──────────┬──────────────────┘
           │ 1:N
           ▼
┌─────────────────────────────┐
│     TRANSACTIONS            │
├─────────────────────────────┤
│ PK id                       │
│ FK user_id                  │   For CASH FLOW tracking only.
│ FK account_id               │   Assets like land/gold are
│ FK to_account_id (nullable) │   updated via direct edit.
│    amount (15,2)            │
│    type (income/expense/    │
│          transfer)          │
│    category                 │
│    date (indexed)           │
│    description              │
│    tags (ARRAY)             │
│    created_at               │
└─────────────────────────────┘

INVESTMENT MODELS (auto-sync to accounts):

┌─────────────────────────┐  ┌─────────────────────────┐
│   STOCK_HOLDINGS        │  │  REAL_ESTATE_PROPERTIES  │
├─────────────────────────┤  ├─────────────────────────┤
│ PK id, FK user_id       │  │ PK id, FK user_id       │
│    ticker, name         │  │    name, location        │
│    shares (15,4)        │  │    property_type         │
│    avg_cost (15,2)      │  │    cost_basis (15,2)     │
│    current_price (15,2) │  │    estimated_value       │
│    sector               │  │    monthly_rent (15,2)   │
│  → category=investment  │  │    area_size, notes      │
│  → balance=shares*price │  │  → category=property     │
└─────────────────────────┘  │  → balance=est_value     │
                             └─────────────────────────┘

┌─────────────────────────┐  ┌─────────────────────────┐
│   BUSINESS_INTERESTS    │  │   GOLD_HOLDINGS         │
├─────────────────────────┤  ├─────────────────────────┤
│ PK id, FK user_id       │  │ PK id, FK user_id       │
│    name                 │  │    description           │
│    equity_percent (5,2) │  │    weight_vori (10,4)    │
│    invested_value       │  │    weight_gram (10,4)    │
│    current_value        │  │    karat (21/22/24)      │
│    annual_income        │  │    buy_price_per_vori    │
│    roi_percent, notes   │  │    current_price_vori    │
│  → category=business    │  │    owner, notes          │
│  → balance=current_val  │  │  → category=gold         │
└─────────────────────────┘  │  → balance=weight*price  │
                             └─────────────────────────┘

┌─────────────────────────┐
│   VEHICLES              │
├─────────────────────────┤
│ PK id, FK user_id       │
│    name, vehicle_type   │
│    purchase_price       │
│    current_value        │
│    monthly_income       │
│    notes                │
│  → category=vehicle     │
│  → balance=current_val  │
└─────────────────────────┘

┌──────────────────────────────┐
│   INTEREST_ENTRIES           │
├──────────────────────────────┤
│ PK id, FK user_id            │
│    source, fiscal_year       │
│    gross_amount (15,2)       │
│    tax_deducted (15,2)       │
│    charges (15,2)            │
│    net_amount (15,2)         │
│    date, notes               │
│    is_distributed            │
│    distributed_to            │
│    distributed_date          │
└──────────────────────────────┘

┌──────────────────────────────┐
│   NET_WORTH_SNAPSHOTS        │
├──────────────────────────────┤
│ PK id, FK user_id            │
│    date (unique w/ user)     │
│    total_assets (15,2)       │
│    total_liabilities (15,2)  │
│    net_worth (15,2)          │
│    breakdown (JSONB)         │
└──────────────────────────────┘
```

## Default Segments

```
Cash & Bank    (asset)     - Bank accounts, cash, FDRs
Investments    (asset)     - Stocks, mutual funds
Property       (asset)     - Real estate, land
Gold           (asset)     - Gold/silver holdings
Vehicles       (asset)     - Bikes, cars, commercial vehicles
Business       (asset)     - Business interests, equity stakes
Other Assets   (asset)     - Electronics, furniture, books, livestock
Liabilities    (liability) - Borrowed, funds, lent money
```

## Edit-First vs Transaction-First

```
METHOD 1: DIRECT EDIT (for assets/liabilities)
  Click Edit → change balance → Save
  → PUT /accounts/{id} or PUT /investments/X/{id}
  → Recalculate segment total
  USE FOR: Land values, gold prices, stock prices, loan balances

METHOD 2: TRANSACTION (for cash flow)
  Create transaction → auto-update account balance
  → POST /transactions
  → income: balance += amount
  → expense: balance -= amount
  → transfer: from -= / to +=
  USE FOR: Salary, rent, groceries, dividends, transfers
```

## Interest Tracking (Islamic Finance)

```
Bank pays interest → Record entry → Auto-add to Interest Fund liability
When distributing  → Mark distributed → Decrease fund balance

Interest Fund tracks:
  - Total accumulated per fiscal year
  - Tax deducted at source
  - Distribution to recipients
  - Undistributed balance (needs to be given away)
```
