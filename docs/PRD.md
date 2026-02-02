# AssetFlow - Product Requirements Document

**Version:** 2.0
**Date:** 2026-01-31
**Product:** AssetFlow - Personal Asset Management SaaS
**Author:** Product & Design

---

## 1. Vision

AssetFlow is a personal asset management platform that gives individuals a complete, real-time picture of their financial position. It follows the **"One Purse"** philosophy: all assets, liabilities, investments, and cash flows are unified into a single hierarchical view, enabling accurate net worth tracking, informed financial decisions, and Islamic zakat compliance.

---

## 2. Problem Statement

### Current Issues Identified

1. **Inconsistent calculations**: Net worth, total assets, and total liabilities are computed independently across dashboard, balance sheet, net worth report, and portfolio endpoints. Each endpoint re-queries and re-sums from scratch, leading to potential drift when segment balances are stale or when investment-linked accounts are not yet synced.

2. **Liabilities not surfaced properly**: The dashboard shows `total_liabilities` in the API response but the frontend only displays four stat cards (Net Worth, Total Assets, Monthly Income, Monthly Expense). Liabilities have no dedicated visibility on the main dashboard. Users cannot see outstanding loans, credit card balances, or mortgage amounts at a glance.

3. **Double-counting risk**: Segment (parent) accounts carry a `balance` that is the sum of children. When reports sum ALL active accounts (including segments), segment balances are double-counted with their children. The reports must exclude `is_segment=True` accounts or only sum leaf accounts.

4. **No inline editing**: Users must navigate away from the dashboard to update account balances, transaction details, or investment values. There is no way to quickly correct a number without full page navigation.

5. **Missing liability lifecycle**: No support for tracking loan payments reducing principal, interest accrual, credit card statement cycles, or mortgage amortization schedules.

---

## 3. Users & Personas

| Persona | Description | Key Need |
|---------|-------------|----------|
| **Salaried Professional** | Steady income, bank accounts, maybe a mortgage and car loan | See net worth after debts, track monthly savings rate |
| **Investor** | Stocks, real estate, business stakes | Portfolio performance vs liabilities (margin loans, mortgages on investment properties) |
| **Small Business Owner** | Business equity + personal assets mixed | Separate business liabilities from personal, unified net worth |
| **Zakat-Conscious Muslim** | Must calculate annual zakat on net zakatable wealth | Accurate zakatable asset total minus qualifying debts |

---

## 4. Features & Requirements

### 4.1 Calculation Engine (Critical Fix)

**Problem:** Calculations are inconsistent across endpoints and double-count segment balances.

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| CALC-01 | Create a single `CalculationService` that all endpoints use for net worth, total assets, total liabilities | P0 |
| CALC-02 | Exclude `is_segment=True` accounts from all summation queries to prevent double-counting parent + children | P0 |
| CALC-03 | Net Worth = SUM(leaf asset balances) - SUM(leaf liability balances) | P0 |
| CALC-04 | Total Assets = SUM(leaf accounts where type="asset") | P0 |
| CALC-05 | Total Liabilities = SUM(leaf accounts where type="liability") | P0 |
| CALC-06 | Monthly Savings Rate = (Monthly Income - Monthly Expense) / Monthly Income * 100 | P1 |
| CALC-07 | Debt-to-Asset Ratio = Total Liabilities / Total Assets * 100 | P1 |
| CALC-08 | Investment gain/loss must be consistent between portfolio endpoint and account balances | P1 |

### 4.2 Liabilities Management

**Problem:** Liabilities exist in the data model but lack proper tracking, categorization, and dashboard visibility.

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| LIAB-01 | Dashboard must show Total Liabilities as a dedicated stat card | P0 |
| LIAB-02 | Dashboard must show Liability Breakdown chart (donut/bar by category: mortgage, loan, credit card) | P1 |
| LIAB-03 | Liability accounts must support: original_amount, interest_rate, minimum_payment, due_date fields | P1 |
| LIAB-04 | Liability categories: mortgage, auto_loan, student_loan, personal_loan, credit_card, line_of_credit, other | P1 |
| LIAB-05 | Balance sheet must clearly separate current liabilities (credit cards, bills due) from long-term liabilities (mortgage, loans) | P2 |
| LIAB-06 | Zakat calculation should subtract qualifying short-term debts from zakatable wealth | P1 |

### 4.3 Dashboard Enhancements

**Problem:** Dashboard is read-only, missing liabilities, and lacks actionable quick-edit capability.

**Requirements:**

| ID | Requirement | Priority |
|----|-------------|----------|
| DASH-01 | Add 6-card stat grid: Net Worth, Total Assets, Total Liabilities, Monthly Income, Monthly Expense, Savings Rate | P0 |
| DASH-02 | Each stat card displays an inline **Edit** button (pencil icon) that enables in-place value editing | P0 |
| DASH-03 | Clicking Edit on a stat card opens an inline form to update the underlying account balance or transaction amount | P0 |
| DASH-04 | Edit mode: clicking the pencil on "Total Assets" expands a mini-list of asset accounts with editable balance fields | P0 |
| DASH-05 | Edit mode: clicking the pencil on "Total Liabilities" expands a mini-list of liability accounts with editable balance fields | P0 |
| DASH-06 | Add Liability Allocation donut chart alongside Asset Allocation | P1 |
| DASH-07 | Add Net Worth trend sparkline (last 6 data points) in the Net Worth stat card | P2 |
| DASH-08 | Recent transactions list should support inline edit (click amount or description to edit) | P1 |
| DASH-09 | Add quick-add buttons: "+ Asset", "+ Liability", "+ Transaction" at top of dashboard | P1 |

### 4.4 Account Management

| ID | Requirement | Priority |
|----|-------------|----------|
| ACCT-01 | Account list/purse view must show liabilities segment with accurate totals | P0 |
| ACCT-02 | Account creation form must support liability-specific fields (interest_rate, minimum_payment, due_date) | P1 |
| ACCT-03 | Account detail view must show payment history for liability accounts | P2 |
| ACCT-04 | Batch balance update: update multiple account balances from a single form | P2 |

### 4.5 Reports & Analytics

| ID | Requirement | Priority |
|----|-------------|----------|
| RPT-01 | All report endpoints must use the centralized CalculationService | P0 |
| RPT-02 | Balance sheet must exclude segment accounts from line items (only show leaf accounts) | P0 |
| RPT-03 | Add Debt Payoff Projection report (snowball/avalanche methods) | P2 |
| RPT-04 | Net worth history must store snapshots (not just current-day point) | P1 |
| RPT-05 | Income vs Expense report must include "Net Savings" metric | P1 |

### 4.6 Investment Calculations

| ID | Requirement | Priority |
|----|-------------|----------|
| INV-01 | Stock gain/loss: (current_price - avg_cost) * shares, consistent everywhere | P0 |
| INV-02 | Real estate: track both property value appreciation AND rental yield | P1 |
| INV-03 | Real estate: support mortgage as linked liability (property value - mortgage balance = equity) | P1 |
| INV-04 | Business: gain/loss = current_value - invested_value, ROI% = gain_loss / invested_value * 100 | P0 |
| INV-05 | Portfolio total must match sum of investment-linked account balances | P0 |

### 4.7 Zakat Calculation (Enhanced)

| ID | Requirement | Priority |
|----|-------------|----------|
| ZKT-01 | Deduct short-term liabilities (due within lunar year) from zakatable wealth | P1 |
| ZKT-02 | Show breakdown: gross zakatable assets, deductible debts, net zakatable wealth, zakat due | P1 |
| ZKT-03 | Exclude personal-use assets (primary residence, personal vehicle) from zakatable wealth | P1 |

---

## 5. Calculation Formulas Reference

### Core Financial Metrics

```
Net Worth = Total Assets - Total Liabilities

Total Assets = SUM(balance) WHERE type="asset" AND is_segment=false AND is_active=true
Total Liabilities = SUM(balance) WHERE type="liability" AND is_segment=false AND is_active=true

Monthly Savings Rate = ((Monthly Income - Monthly Expense) / Monthly Income) * 100
Debt-to-Asset Ratio = (Total Liabilities / Total Assets) * 100
```

### Investment Metrics

```
Stock Market Value = shares * current_price
Stock Cost Basis = shares * avg_cost
Stock Gain/Loss = Market Value - Cost Basis
Stock Gain/Loss % = (Gain/Loss / Cost Basis) * 100

Real Estate Equity = estimated_value - linked_mortgage_balance
Real Estate Rental Yield = (monthly_rent * 12) / estimated_value * 100

Business ROI = ((current_value - invested_value) / invested_value) * 100
Business Gain/Loss = current_value - invested_value

Portfolio Total = SUM(stock market values) + SUM(real estate values) + SUM(business current values)
Portfolio Gain/Loss = SUM(individual gain/losses)
```

### Zakat (Enhanced)

```
Gross Zakatable = cash_and_bank + stock_market_values + business_current_values + rental_income_accumulated
Deductible Debts = SUM(liability balances WHERE due within hawl AND category IN [loan, credit_card, personal_loan])
Net Zakatable = Gross Zakatable - Deductible Debts
Zakat Due = Net Zakatable * 0.025 (if Net Zakatable >= nisab)
```

---

## 6. Dashboard Edit Mode - Interaction Design

### Edit Button Behavior

1. Each stat card has a subtle pencil icon in the top-right corner
2. Clicking the pencil toggles the card into "edit mode"
3. In edit mode, the stat card expands to show the constituent accounts
4. Each account row shows: name, current balance, editable input field
5. User modifies values and clicks "Save" (checkmark) or "Cancel" (X)
6. On save: PATCH the account balance via API, recalculate segment, refresh dashboard data
7. On cancel: revert to original values, collapse back to summary view

### Recent Transactions Inline Edit

1. Click on a transaction amount or description to make it editable
2. Shows an inline text input with the current value
3. Press Enter or click away to save
4. Press Escape to cancel

---

## 7. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| API response time | < 200ms for dashboard summary |
| Calculation consistency | All endpoints return identical net worth for same data state |
| Data integrity | Segment balances always equal sum of active children |
| Concurrent safety | Optimistic locking on balance updates |

---

## 8. Out of Scope (v2.0)

- Multi-currency conversion with live exchange rates
- Automated bank account syncing (Plaid/Yodlee)
- Tax calculation and filing
- Shared/family accounts
- Mobile native app (web-responsive only)

---

## 9. Success Metrics

| Metric | Target |
|--------|--------|
| Calculation accuracy | 100% consistency across all endpoints |
| Dashboard completeness | Assets + Liabilities + Income + Expense + Savings Rate visible |
| Edit efficiency | Update any balance in < 3 clicks from dashboard |
| Liability visibility | All liability categories tracked and surfaced |
