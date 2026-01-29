"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { reportsApi } from "@/lib/api";
import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardTitle } from "@/components/ui/card";
import { DonutChart } from "@/components/charts/donut-chart";
import { DollarSign, TrendingUp, TrendingDown, Wallet } from "lucide-react";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function DashboardPage() {
  const { token, user } = useAuth();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    if (token) {
      reportsApi.dashboard(token).then(setData).catch(console.error);
    }
  }, [token]);

  if (!data) {
    return <div className="flex items-center justify-center h-64"><span className="font-mono text-xs text-neutral-400 animate-pulse">LOADING</span></div>;
  }

  const currency = user?.currency || "USD";
  const allocation = (data.asset_allocation || []).map((a: any) => ({ name: a.category, value: a.value }));

  return (
    <div className="space-y-8">
      <div>
        <p className="font-mono text-xs tracking-widest text-accent uppercase mb-1">Overview</p>
        <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-px bg-neutral-200 dark:bg-neutral-800">
        <StatCard title="Net Worth" value={data.net_worth} icon={DollarSign} currency={currency} />
        <StatCard title="Total Assets" value={data.total_assets} icon={Wallet} currency={currency} />
        <StatCard title="Monthly Income" value={data.monthly_income} icon={TrendingUp} currency={currency} />
        <StatCard title="Monthly Expense" value={data.monthly_expense} icon={TrendingDown} trend="down" currency={currency} />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardTitle>Asset Allocation</CardTitle>
          <div className="mt-4">
            {allocation.length > 0 ? <DonutChart data={allocation} /> : <p className="text-xs text-neutral-400 py-8 text-center">No assets yet</p>}
          </div>
        </Card>
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
    </div>
  );
}
