"use client";
import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { zakatApi } from "@/lib/api";
import { Card, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatCurrency } from "@/lib/utils";
import { Calculator } from "lucide-react";

export default function ZakatPage() {
  const { token, user } = useAuth();
  const [goldPrice, setGoldPrice] = useState(75);
  const [silverPrice, setSilverPrice] = useState(0.9);
  const [useGold, setUseGold] = useState(true);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const currency = user?.currency || "USD";

  const calculate = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await zakatApi.calculate(token, {
        gold_price_per_gram: goldPrice,
        silver_price_per_gram: silverPrice,
        use_gold_nisab: useGold,
      });
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <p className="font-mono text-xs tracking-widest text-accent uppercase mb-1">Islamic Finance</p>
        <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">Zakat Calculator</h1>
      </div>

      <Card>
        <CardTitle>Configuration</CardTitle>
        <div className="mt-4 space-y-5">
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Gold Price (per gram)</label>
            <Input type="number" step="0.01" value={goldPrice} onChange={e => setGoldPrice(parseFloat(e.target.value) || 0)} />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Silver Price (per gram)</label>
            <Input type="number" step="0.01" value={silverPrice} onChange={e => setSilverPrice(parseFloat(e.target.value) || 0)} />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-3">Nisab Basis</label>
            <div className="flex gap-0">
              <button
                onClick={() => setUseGold(true)}
                className={`px-5 py-2 text-xs font-medium uppercase tracking-wider transition-colors ${useGold ? "bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900" : "border border-neutral-300 text-neutral-500 dark:border-neutral-700"}`}
              >Gold</button>
              <button
                onClick={() => setUseGold(false)}
                className={`px-5 py-2 text-xs font-medium uppercase tracking-wider transition-colors ${!useGold ? "bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900" : "border border-neutral-300 text-neutral-500 dark:border-neutral-700"}`}
              >Silver</button>
            </div>
          </div>
          <Button onClick={calculate} disabled={loading} className="w-full">
            <Calculator size={14} className="mr-2" />
            {loading ? "Calculating..." : "Calculate Zakat"}
          </Button>
        </div>
      </Card>

      {result && (
        <Card>
          <CardTitle>Results</CardTitle>
          <div className="mt-4 space-y-4">
            <div className="grid sm:grid-cols-2 gap-px bg-neutral-100 dark:bg-neutral-800">
              {[
                { label: "Cash & Bank", value: result.breakdown.cash_and_bank },
                { label: "Investments", value: result.breakdown.investments },
                { label: "Rental Income", value: result.breakdown.real_estate_rent_income },
                { label: "Business", value: result.breakdown.business_interests },
              ].map(item => (
                <div key={item.label} className="bg-white dark:bg-neutral-900 p-4">
                  <p className="text-xs uppercase tracking-wider text-neutral-400">{item.label}</p>
                  <p className="font-mono text-lg font-bold mt-1 text-neutral-900 dark:text-neutral-100">{formatCurrency(item.value, currency)}</p>
                </div>
              ))}
            </div>
            <div className="border-t border-neutral-200 dark:border-neutral-800 pt-4 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs uppercase tracking-wider text-neutral-400">Total Zakatable</span>
                <span className="font-mono text-sm font-bold text-neutral-900 dark:text-neutral-100">{formatCurrency(result.breakdown.total_zakatable, currency)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs uppercase tracking-wider text-neutral-400">Nisab Threshold</span>
                <span className="font-mono text-sm text-neutral-500">{formatCurrency(result.breakdown.nisab_threshold, currency)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs uppercase tracking-wider text-neutral-400">Above Nisab</span>
                <span className={`font-mono text-xs font-medium uppercase ${result.breakdown.is_above_nisab ? "text-neutral-900 dark:text-neutral-100" : "text-neutral-400"}`}>
                  {result.breakdown.is_above_nisab ? "Yes" : "No"}
                </span>
              </div>
              <div className="flex justify-between items-center pt-3 border-t border-neutral-200 dark:border-neutral-800">
                <span className="text-sm font-bold text-neutral-900 dark:text-neutral-100">Zakat Due (2.5%)</span>
                <span className="font-mono text-lg font-bold text-accent">{formatCurrency(result.breakdown.zakat_due, currency)}</span>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
