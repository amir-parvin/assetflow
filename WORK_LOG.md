# AssetFlow - Work Log

## Overview

Personal asset management SaaS application. Stack: FastAPI (Python 3.13) + Next.js 14 (TypeScript) + PostgreSQL + Redis + Docker Compose. Deployed on Kubernetes homelab with Traefik ingress.

- Frontend: https://assetflow.alamin.rocks
- API: https://assetflow-api.alamin.rocks

## Architecture

### "One Purse" Model

The core concept is a unified financial view: one purse with segments and sub-segments.

- **Purse**: The user's entire financial picture
- **Segments**: Top-level categories (Cash & Bank, Investments, Property, Business, Liabilities) - auto-created per user
- **Sub-segments**: Individual accounts/holdings within each segment

When investments (stocks, real estate, business interests) are created, they automatically sync as sub-segments under the appropriate parent segment. This ensures the purse always reflects the complete picture without manual duplication.

### Backend

```
backend/app/
├── core/           # Config, database, security (JWT + bcrypt)
├── models/         # SQLAlchemy 2.0 async models
│   ├── user.py     # User with currency preference
│   ├── account.py  # Account with parent_id (segment/sub-segment hierarchy)
│   ├── transaction.py
│   └── investment.py   # StockHolding, RealEstateProperty, BusinessInterest
├── schemas/        # Pydantic v2 schemas
├── api/            # FastAPI route handlers
│   ├── auth.py     # Register, login, refresh, me, update profile
│   ├── accounts.py # CRUD + /purse endpoint (segment view)
│   ├── transactions.py
│   ├── investments.py  # CRUD with auto-sync to account segments
│   ├── reports.py      # Net worth, balance sheet, income/expense, cash flow, dashboard
│   └── zakat.py        # Zakat calculator with gold/silver nisab
└── tests/
```

Key technical decisions:
- Direct `bcrypt` usage (passlib is unmaintained, breaks on Python 3.13)
- `import datetime as dt` pattern to avoid Pydantic field name shadowing
- Account model has `parent_id` (self-referential FK), `source_type`/`source_id` for investment linkage
- `is_segment` flag distinguishes top-level segments from sub-segments

### Frontend

```
frontend/src/
├── app/
│   ├── (auth)/         # Login, Register (with currency selector)
│   ├── (dashboard)/    # Protected routes
│   │   ├── dashboard/  # Overview stats, allocation chart, recent transactions
│   │   ├── accounts/   # Purse view - segments with nested sub-segments
│   │   ├── transactions/
│   │   ├── reports/
│   │   ├── investments/
│   │   ├── zakat/
│   │   └── settings/   # Currency selector, profile update
│   └── page.tsx        # Landing page
├── components/
│   ├── ui/             # Button, Card, Input, Select, Modal
│   ├── charts/         # DonutChart, AreaChart, BarChart (Recharts)
│   └── dashboard/      # Sidebar, StatCard
├── hooks/useAuth.ts
└── lib/
    ├── api.ts          # Full API client
    └── utils.ts        # cn(), formatCurrency(), formatDate()
```

### Design Language

Inspired by alamin.rocks aesthetic:
- **No rounded corners** - sharp geometric edges throughout
- **Grayscale palette** with golden yellow accent (#E5C07B)
- **Typography**: Inter (sans) + JetBrains Mono (monospace for numbers/labels)
- **Uppercase tracking-widest** for section labels and navigation
- **Grid gap-px** pattern for card grids (1px gap creates subtle borders)
- **Geometric decoration**: `//` prefix markers, accent underline bars
- **Minimal color**: black/white for emphasis, neutral-400 for secondary, accent for highlights
- **Dark mode**: full support, inverted primary (dark bg, light text)

### Infrastructure

- Docker Compose for local dev (postgres, redis, backend, frontend)
- Kubernetes manifests in homelab repo (`~/src/homelab/k8s/apps/assetflow/`)
- Traefik IngressRoute with HTTPS (Let's Encrypt)
- Harbor private registry at registry.homelab.alamin.rocks

## Completed

1. Full backend API: auth, accounts (purse model), transactions, investments, reports, zakat
2. Frontend: landing, auth, dashboard, purse/accounts, transactions, reports, investments, zakat, settings
3. Investment auto-sync to purse segments
4. Currency selector (registration + settings)
5. UI redesign with alamin.rocks design language
6. K8s deployment with Traefik ingress
7. Docker images built and pushed to private registry

## Deployment

```bash
# Build and push
docker build -t registry.homelab.alamin.rocks/assetflow/backend:latest backend/
docker push registry.homelab.alamin.rocks/assetflow/backend:latest
docker build -t registry.homelab.alamin.rocks/assetflow/frontend:latest frontend/
docker push registry.homelab.alamin.rocks/assetflow/frontend:latest

# Apply k8s manifests
kubectl apply -f ~/src/homelab/k8s/apps/assetflow/

# Restart deployments
kubectl rollout restart deployment/assetflow-backend -n assetflow
kubectl rollout restart deployment/assetflow-frontend -n assetflow
```
