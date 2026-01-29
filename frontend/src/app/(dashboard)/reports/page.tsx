"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { reportsApi } from "@/lib/api";
import { Card, CardTitle } from "@/components/ui/card";
import { BarChart } from "@/components/charts/bar-chart";
import { formatCurrency } from "@/lib/utils";

export default function ReportsPage() {
  const { token, user } = useAuth();
  const [balanceSheet, setBalanceSheet] = useState<any>(null);
  const [incomeExpense, setIncomeExpense] = useState<any>(null);
  const [cashFlow, setCashFlow] = useState<any>(null);

  const currency = user?.currency || "USD";

  useEffect(() => {
    if (!token) return;
    reportsApi.balanceSheet(token).then(setBalanceSheet).catch(console.error);
    reportsApi.incomeExpense(token, 6).then(setIncomeExpense).catch(console.error);
    reportsApi.cashFlow(token, 6).then(setCashFlow).catch(console.error);
  }, [token]);

  return (
    <div className="space-y-8">
      <div>
        <p className="font-mono text-xs tracking-widest text-accent uppercase mb-1">Analytics</p>
        <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">Reports</h1>
      </div>

      {balanceSheet && (
        <div className="grid sm:grid-cols-3 gap-px bg-neutral-200 dark:bg-neutral-800">
          <div className="bg-white dark:bg-neutral-900 p-5">
            <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">Total Assets</p>
            <p className="mt-1 font-mono text-xl font-bold text-neutral-900 dark:text-neutral-100">{formatCurrency(balanceSheet.total_assets, currency)}</p>
          </div>
          <div className="bg-white dark:bg-neutral-900 p-5">
            <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">Total Liabilities</p>
            <p className="mt-1 font-mono text-xl font-bold text-red-600">{formatCurrency(balanceSheet.total_liabilities, currency)}</p>
          </div>
          <div className="bg-white dark:bg-neutral-900 p-5">
            <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">Net Worth</p>
            <p className="mt-1 font-mono text-xl font-bold text-neutral-900 dark:text-neutral-100">{formatCurrency(balanceSheet.net_worth, currency)}</p>
          </div>
        </div>
      )}

      {incomeExpense && (
        <Card>
          <CardTitle>Income vs Expense</CardTitle>
          <div className="grid sm:grid-cols-3 gap-6 mt-4 mb-6">
            <div>
              <p className="text-xs uppercase tracking-wider text-neutral-400">Income</p>
              <p className="font-mono text-lg font-bold text-neutral-900 dark:text-neutral-100">{formatCurrency(incomeExpense.total_income, currency)}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-neutral-400">Expense</p>
              <p className="font-mono text-lg font-bold text-neutral-400">{formatCurrency(incomeExpense.total_expense, currency)}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-neutral-400">Net</p>
              <p className="font-mono text-lg font-bold">{formatCurrency(incomeExpense.net, currency)}</p>
            </div>
          </div>
          {incomeExpense.by_category.length > 0 && (
            <BarChart
              data={incomeExpense.by_category}
              bars={[
                { dataKey: "income", color: "#171717", name: "Income" },
                { dataKey: "expense", color: "#a3a3a3", name: "Expense" },
              ]}
              xKey="category"
            />
          )}
        </Card>
      )}

      {cashFlow && cashFlow.data.length > 0 && (
        <Card>
          <CardTitle>Cash Flow</CardTitle>
          <div className="mt-4">
            <BarChart
              data={cashFlow.data}
              bars={[
                { dataKey: "inflow", color: "#171717", name: "Inflow" },
                { dataKey: "outflow", color: "#d4d4d4", name: "Outflow" },
              ]}
              xKey="period"
            />
          </div>
        </Card>
      )}
    </div>
  );
}
