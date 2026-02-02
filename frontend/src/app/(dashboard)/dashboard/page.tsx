"use client";
import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/hooks/useAuth";
import { reportsApi, accountsApi } from "@/lib/api";
import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardTitle } from "@/components/ui/card";
import { DonutChart } from "@/components/charts/donut-chart";
import { DollarSign, TrendingUp, TrendingDown, Wallet, CreditCard, PiggyBank, X, Check } from "lucide-react";
import { formatCurrency, formatDate } from "@/lib/utils";

interface EditableAccount {
  id: number;
  name: string;
  balance: number;
  type: string;
  category: string;
}

export default function DashboardPage() {
  const { token, user } = useAuth();
  const [data, setData] = useState<any>(null);
  const [editMode, setEditMode] = useState<"assets" | "liabilities" | null>(null);
  const [accounts, setAccounts] = useState<EditableAccount[]>([]);
  const [editValues, setEditValues] = useState<Record<number, string>>({});
  const [saving, setSaving] = useState(false);

  const loadDashboard = useCallback(() => {
    if (token) {
      reportsApi.dashboard(token).then(setData).catch(console.error);
    }
  }, [token]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const openEditMode = async (mode: "assets" | "liabilities") => {
    if (!token) return;
    const all = await accountsApi.list(token);
    const filtered = all.filter(
      (a: any) => a.type === mode.slice(0, -1) && !a.is_segment && a.is_active
    );
    setAccounts(filtered);
    const vals: Record<number, string> = {};
    filtered.forEach((a: any) => { vals[a.id] = String(a.balance); });
    setEditValues(vals);
    setEditMode(mode);
  };

  const saveEdits = async () => {
    if (!token) return;
    setSaving(true);
    for (const acct of accounts) {
      const newVal = parseFloat(editValues[acct.id] || "0");
      if (newVal !== acct.balance) {
        await accountsApi.update(token, acct.id, { balance: newVal });
      }
    }
    setSaving(false);
    setEditMode(null);
    loadDashboard();
  };

  if (!data) {
    return <div className="flex items-center justify-center h-64"><span className="font-mono text-xs text-neutral-400 animate-pulse">LOADING</span></div>;
  }

  const currency = user?.currency || "USD";
  const assetAlloc = (data.asset_allocation || []).map((a: any) => ({ name: a.category, value: a.value }));
  const liabilityAlloc = (data.liability_allocation || []).map((a: any) => ({ name: a.category, value: a.value }));

  return (
    <div className="space-y-8">
      <div>
        <p className="font-mono text-xs tracking-widest text-accent uppercase mb-1">Overview</p>
        <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-px bg-neutral-200 dark:bg-neutral-800">
        <StatCard title="Net Worth" value={data.net_worth} icon={DollarSign} currency={currency} />
        <StatCard title="Total Assets" value={data.total_assets} icon={Wallet} currency={currency} onEdit={() => openEditMode("assets")} />
        <StatCard title="Total Liabilities" value={data.total_liabilities} icon={CreditCard} trend="down" currency={currency} onEdit={() => openEditMode("liabilities")} />
        <StatCard title="Monthly Income" value={data.monthly_income} icon={TrendingUp} currency={currency} />
        <StatCard title="Monthly Expense" value={data.monthly_expense} icon={TrendingDown} trend="down" currency={currency} />
        <StatCard title="Savings Rate" value={data.savings_rate || 0} icon={PiggyBank} suffix="%" />
      </div>

      {editMode && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <CardTitle>{editMode === "assets" ? "Edit Asset Balances" : "Edit Liability Balances"}</CardTitle>
            <div className="flex items-center gap-2">
              <button onClick={saveEdits} disabled={saving} className="text-green-600 hover:text-green-700 disabled:opacity-50">
                <Check size={16} strokeWidth={2} />
              </button>
              <button onClick={() => setEditMode(null)} className="text-neutral-400 hover:text-neutral-600">
                <X size={16} strokeWidth={2} />
              </button>
            </div>
          </div>
          <div className="space-y-0">
            {accounts.length === 0 && (
              <p className="text-xs text-neutral-400 py-4 text-center">
                No {editMode === "assets" ? "asset" : "liability"} accounts found
              </p>
            )}
            {accounts.map((acct) => (
              <div key={acct.id} className="flex items-center justify-between py-3 border-b border-neutral-100 dark:border-neutral-800 last:border-0">
                <div>
                  <p className="text-sm text-neutral-900 dark:text-neutral-100">{acct.name}</p>
                  <p className="font-mono text-[10px] text-neutral-400 mt-0.5">{acct.category}</p>
                </div>
                <input
                  type="number"
                  step="0.01"
                  value={editValues[acct.id] || ""}
                  onChange={(e) => setEditValues({ ...editValues, [acct.id]: e.target.value })}
                  className="font-mono text-sm text-right w-32 bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 px-2 py-1 text-neutral-900 dark:text-neutral-100 focus:outline-none focus:border-accent"
                />
              </div>
            ))}
          </div>
        </Card>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardTitle>Asset Allocation</CardTitle>
          <div className="mt-4">
            {assetAlloc.length > 0 ? <DonutChart data={assetAlloc} /> : <p className="text-xs text-neutral-400 py-8 text-center">No assets yet</p>}
          </div>
        </Card>
        <Card>
          <CardTitle>Liability Breakdown</CardTitle>
          <div className="mt-4">
            {liabilityAlloc.length > 0 ? <DonutChart data={liabilityAlloc} /> : <p className="text-xs text-neutral-400 py-8 text-center">No liabilities</p>}
          </div>
        </Card>
      </div>

      <Card>
        <CardTitle>Recent Transactions</CardTitle>
        <div className="mt-4 space-y-0">
          {(data.recent_transactions || []).map((t: any) => (
            <div key={t.id} className="flex items-center justify-between py-3 border-b border-neutral-100 dark:border-neutral-800 last:border-0">
              <div>
                <p className="text-sm text-neutral-900 dark:text-neutral-100">{t.description || t.category}</p>
                <p className="font-mono text-[10px] text-neutral-400 mt-0.5">{formatDate(t.date)}</p>
              </div>
              <span className={`font-mono text-sm font-medium ${t.type === "income" ? "text-neutral-900 dark:text-neutral-100" : "text-neutral-400"}`}>
                {t.type === "income" ? "+" : "-"}{formatCurrency(t.amount, currency)}
              </span>
            </div>
          ))}
          {(data.recent_transactions || []).length === 0 && <p className="text-xs text-neutral-400 py-4 text-center">No transactions yet</p>}
        </div>
      </Card>
    </div>
  );
}
