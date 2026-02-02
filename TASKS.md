# AssetFlow - Task Tracker

## Phase 1: Backend Foundation

### T1: Schema Migration - New fields + tables
- **Branch:** `feat/t1-schema-migration`
- **Status:** TODO
- **What:**
  - Add to Account: `sub_category`, `notes`
  - Add to Transaction: `to_account_id` (FK nullable)
  - Add to RealEstateProperty: `cost_basis`, `area_size`, `notes`
  - Add to BusinessInterest: `roi_percent`, `notes`
  - Create GoldHolding model (weight_vori, weight_gram, karat, buy/current price, owner, notes)
  - Create Vehicle model (name, type, purchase_price, current_value, monthly_income, notes)
  - Create InterestEntry model (source, fiscal_year, gross/tax/charges/net, distribution fields)
  - Create NetWorthSnapshot model (date, assets, liabilities, net_worth, breakdown JSONB)
  - Update DEFAULT_SEGMENTS: add Gold, Vehicles, Other Assets
- **Test:** `alembic upgrade head` passes. Models instantiate with new fields.
- **Success:** Clean migration, no errors.

### T2: Gold Holdings API + Auto-Sync
- **Branch:** `feat/t2-gold-api`
- **Status:** TODO
- **Depends on:** T1
- **What:** CRUD for gold holdings. Auto-sync to Gold segment (balance = weight * current_price_per_vori).
- **Test:**
  - Create gold → syncs to Gold segment with correct value
  - Update current_price → balance updates
  - Delete → removes from segment
  - Weight in vori or grams both work
- **Success:** 4 test cases pass.

### T3: Vehicle API + Auto-Sync
- **Branch:** `feat/t3-vehicle-api`
- **Status:** TODO
- **Depends on:** T1
- **What:** CRUD for vehicles. Auto-sync to Vehicles segment.
- **Test:**
  - Create vehicle → syncs to Vehicles segment
  - Update current_value → balance updates
  - monthly_income tracked correctly
- **Success:** 3 test cases pass.

### T4: Interest Tracking API (Islamic Finance)
- **Branch:** `feat/t4-interest-tracking`
- **Status:** TODO
- **Depends on:** T1
- **What:** CRUD for interest entries. Record interest received, track distribution. Auto-update interest fund liability balance.
- **Test:**
  - Record interest → fund balance increases
  - Mark as distributed → fund balance decreases
  - Fiscal year summary aggregation works
  - Undistributed total is correct
- **Success:** 4 test cases pass.

### T5: Transaction-Balance Integration + Transfers
- **Branch:** `feat/t5-txn-balance`
- **Status:** TODO
- **Depends on:** T1
- **What:** Transactions auto-update account balances. Transfer type requires to_account_id. Balance cascades to segments.
- **Test:**
  - Income → balance increases
  - Expense → balance decreases
  - Transfer → source decreases, dest increases
  - Delete → reverts balance
  - Segment recalculates
- **Success:** 5 test cases pass.

### T6: Pagination + Net Worth Snapshots + Monthly Summary
- **Branch:** `feat/t6-pagination-snapshots`
- **Status:** TODO
- **Depends on:** T1, T5
- **What:**
  - Paginated transaction list: `{items, total, page, per_page}`
  - Net worth snapshot on dashboard access (if none today)
  - Monthly summary endpoint aggregating transactions by month
- **Test:**
  - Pagination returns correct page with total count
  - Snapshot created automatically on first access
  - Monthly summary matches transaction totals
- **Success:** All 3 features working.

### T7: Seed Data Script (Holdings.pdf)
- **Branch:** `feat/t7-seed-data`
- **Status:** TODO
- **Depends on:** T1-T6
- **What:** Python script populating ALL data from Holdings.pdf:
  - User: alamin, currency BDT
  - Bank accounts: Deel, Payoneer, TransferWise, Janata, IBBL, Asia Islami, City General/Delight/Islamic, DBBL, LBSL, Bkash
  - 11 real estate properties with cost, estimated value, rent, area, Bengali notes
  - 4 business interests: City Care Hospital 7%, Venture with Faria, AK2 Technologies, Alisha Noor
  - Gold: ~5.44 vori across 3 owners (আম্মু, আসমা, অনামিকা)
  - 2 vehicles: Fazer, Suzuki Gixxer SF
  - Other assets: Electronics ৳1.65M, Furniture ৳277.5K, Books ৳105K, Livestock ৳36K
  - Liabilities: 5 borrowed entries, 2 interest funds, zakat fund, 3 lent-out entries
  - Interest history: FY 2020-21 through FY 2023-24
  - Monthly earnings/expenses: Dec 2017 - Dec 2022 (as transactions)
  - Zakat net worth snapshots: 2019-2025
- **Test:**
  - Script runs on clean DB without errors
  - GET /accounts/purse returns 8 segments with correct sub-segments
  - Net worth ≈ ৳27.7M
  - All 11 properties visible with Bengali names
  - Interest fund totals match PDF
- **Success:** Full purse matches Holdings.pdf.

---

## Phase 2: Frontend

### T8: Toast Notification System
- **Branch:** `feat/t8-toast`
- **Status:** TODO
- **What:** Toast context + provider. Success/error/warning toasts on all API calls.
- **Files:** `components/ui/toast.tsx`, dashboard layout
- **Test:** Toasts appear on CRUD ops, auto-dismiss 3s, stack properly.
- **Success:** Visual confirmation on all operations.

### T9: Liabilities Page
- **Branch:** `feat/t9-liabilities-page`
- **Status:** TODO
- **Depends on:** T4, T8
- **What:** New page with 4 sections:
  - Borrowed (with [Pay] action → creates transaction, reduces balance)
  - Interest Funds (with [Distribute] action, haram warning indicator)
  - Zakat Fund (with [Distribute] action)
  - Lent Money (with [Got Back] action)
  - Each with add/edit/notes support
- **Test:**
  - All 4 sections render with correct data from seed
  - Add/edit/delete works per section
  - [Pay] creates transaction and reduces balance
  - Interest funds visually distinct with warning
- **Success:** Page matches architecture wireframe.

### T10: Gold + Vehicle UI in Investments Page
- **Branch:** `feat/t10-gold-vehicle-ui`
- **Status:** TODO
- **Depends on:** T2, T3, T8
- **What:** Add Gold Holdings section (weight vori/gram, karat, owner, value) and Vehicles section (name, type, value, income) to investments page with Add/Edit modals.
- **Test:**
  - Gold section shows holdings with vori/gram display
  - Vehicle section shows with type badge
  - Add/Edit modals work for both
  - Auto-sync to purse verified
- **Success:** Both new asset classes fully functional in UI.

### T11: Monthly Income/Expense Page
- **Branch:** `feat/t11-income-expense`
- **Status:** TODO
- **Depends on:** T6, T8
- **What:** New page with month navigator (< Month >), income/expense/savings cards, category breakdown with horizontal bars, 12-month trend BarChart.
- **Test:**
  - Month navigation (prev/next) works
  - Totals match transactions for selected month
  - Category breakdown renders with bars
  - Bar chart shows 12 months of data
- **Success:** Matches wireframe from architecture doc.

### T12: Edit Modals for All Entities
- **Branch:** `feat/t12-edit-modals`
- **Status:** TODO
- **Depends on:** T8
- **What:** Add edit functionality for accounts, transactions, stocks, real estate, business interests. Currently only create+delete exist.
- **Test:**
  - Click entity → opens pre-filled edit modal
  - Save → PUT request → data refreshes
  - Toast on success/error
- **Success:** Every entity type has working edit UI.

### T13: Investment Modals - Real Estate/Business Enhancements
- **Branch:** `feat/t13-investment-modals`
- **Status:** TODO
- **Depends on:** T8, T12
- **What:** Add Real Estate and Business create/edit modals with new fields (cost_basis, area_size, roi_percent, notes). Real estate shows rental income. Business shows ROI.
- **Test:**
  - Real Estate modal has cost/value/rent/area/notes fields
  - Business modal has equity/invested/current/roi/notes
  - Data persists and auto-syncs to purse
- **Success:** All investment types have full CRUD modals.

### T14: Pagination UI + Date Filters for Transactions
- **Branch:** `feat/t14-pagination-filters`
- **Status:** TODO
- **Depends on:** T6, T8
- **What:** Prev/next pagination controls with page indicator. Date range filter (from/to). Category filter improvements.
- **Test:**
  - Pagination visible when >10 items
  - Date range filter works correctly
  - Resets to page 1 on filter change
- **Success:** Can navigate large transaction lists efficiently.

---

## Phase 3: Polish

### T15: Backend Test Suite
- **Branch:** `feat/t15-tests`
- **Status:** TODO
- **Depends on:** T1-T7
- **What:** Comprehensive tests for all new features: gold, vehicles, interests, transfers, pagination, snapshots, seed data verification.
- **Test:** All endpoints have happy path + error case tests.
- **Success:** `pytest` passes with full coverage of new features.

### T16: Reports Enhancements - Charts + Zakat History
- **Branch:** `feat/t16-report-charts`
- **Status:** TODO
- **Depends on:** T6, T8
- **What:**
  - AreaChart on reports page showing net worth over time (from snapshots)
  - Zakat page shows yearly history table with net worth + zakat amounts
  - Interest summary on reports (total accumulated, distributed, pending)
- **Test:**
  - Net worth chart renders with historical seed data
  - Zakat history shows 2019-2025 entries
  - Interest summary shows correct accumulated/distributed amounts
- **Success:** Visual verification with seed data.

---

## Execution Order

```
PHASE 1 - BACKEND                      PHASE 2 - FRONTEND            PHASE 3
──────────────────                      ──────────────────            ────────
T1  Schema Migration ──┐
T2  Gold API           │
T3  Vehicle API        ├──► T7 Seed     T8  Toast System
T4  Interest API       │    Data        T9  Liabilities Page
T5  Txn-Balance        │                T10 Gold+Vehicle UI
T6  Pagination+Reports─┘                T11 Income/Expense Page      T15 Tests
                                        T12 Edit Modals              T16 Charts
                                        T13 Investment Modals
                                        T14 Pagination UI
```

Each task = separate git branch → PR with tests.
All amounts in BDT (৳). Default currency = BDT.
