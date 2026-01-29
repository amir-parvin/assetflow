"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { investmentsApi } from "@/lib/api";
import { Card, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { Plus, Trash2 } from "lucide-react";

export default function InvestmentsPage() {
  const { token, user } = useAuth();
  const [stocks, setStocks] = useState<any[]>([]);
  const [realEstate, setRealEstate] = useState<any[]>([]);
  const [business, setBusiness] = useState<any[]>([]);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [showStockModal, setShowStockModal] = useState(false);
  const [stockForm, setStockForm] = useState({ ticker: "", name: "", shares: 0, avg_cost: 0, current_price: 0, sector: "" });

  const currency = user?.currency || "USD";

  const load = () => {
    if (!token) return;
    investmentsApi.stocks.list(token).then(setStocks).catch(console.error);
    investmentsApi.realEstate.list(token).then(setRealEstate).catch(console.error);
    investmentsApi.business.list(token).then(setBusiness).catch(console.error);
    investmentsApi.portfolio(token).then(setPortfolio).catch(console.error);
  };
  useEffect(load, [token]);

  const addStock = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    await investmentsApi.stocks.create(token, stockForm);
    setShowStockModal(false);
    setStockForm({ ticker: "", name: "", shares: 0, avg_cost: 0, current_price: 0, sector: "" });
    load();
  };

  return (
    <div className="space-y-8">
      <div>
        <p className="font-mono text-xs tracking-widest text-accent uppercase mb-1">Portfolio</p>
        <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">Investments</h1>
        <p className="text-xs text-neutral-400 mt-1">Investments are automatically synced to your purse segments.</p>
      </div>

      {portfolio && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-px bg-neutral-200 dark:bg-neutral-800">
          <div className="bg-white dark:bg-neutral-900 p-5">
            <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">Portfolio</p>
            <p className="mt-1 font-mono text-lg font-bold text-neutral-900 dark:text-neutral-100">{formatCurrency(portfolio.total_portfolio_value, currency)}</p>
          </div>
          <div className="bg-white dark:bg-neutral-900 p-5">
            <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">Stocks</p>
            <p className="mt-1 font-mono text-lg font-bold text-neutral-900 dark:text-neutral-100">{formatCurrency(portfolio.total_stocks_value, currency)}</p>
          </div>
          <div className="bg-white dark:bg-neutral-900 p-5">
            <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">Real Estate</p>
            <p className="mt-1 font-mono text-lg font-bold text-neutral-900 dark:text-neutral-100">{formatCurrency(portfolio.total_real_estate_value, currency)}</p>
          </div>
          <div className="bg-white dark:bg-neutral-900 p-5">
            <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">Gain / Loss</p>
            <p className={`mt-1 font-mono text-lg font-bold ${portfolio.total_gain_loss >= 0 ? "text-neutral-900 dark:text-neutral-100" : "text-red-600"}`}>
              {formatCurrency(portfolio.total_gain_loss, currency)}
            </p>
          </div>
        </div>
      )}

      <Card>
        <div className="flex items-center justify-between mb-4">
          <CardTitle>Stock Holdings</CardTitle>
          <Button size="sm" onClick={() => setShowStockModal(true)}><Plus size={13} className="mr-1" /> Add</Button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-800 text-left">
                <th className="py-2 px-3 text-xs font-medium uppercase tracking-wider text-neutral-400">Ticker</th>
                <th className="py-2 px-3 text-xs font-medium uppercase tracking-wider text-neutral-400">Name</th>
                <th className="py-2 px-3 text-xs font-medium uppercase tracking-wider text-neutral-400 text-right">Shares</th>
                <th className="py-2 px-3 text-xs font-medium uppercase tracking-wider text-neutral-400 text-right">Value</th>
                <th className="py-2 px-3 text-xs font-medium uppercase tracking-wider text-neutral-400 text-right">G/L</th>
                <th className="py-2 px-3 w-8"></th>
              </tr>
            </thead>
            <tbody>
              {stocks.map(s => (
                <tr key={s.id} className="border-b border-neutral-100 dark:border-neutral-800">
                  <td className="py-2 px-3 font-mono text-xs font-medium text-neutral-900 dark:text-neutral-100">{s.ticker}</td>
                  <td className="py-2 px-3 text-neutral-500">{s.name}</td>
                  <td className="py-2 px-3 text-right font-mono text-xs">{s.shares}</td>
                  <td className="py-2 px-3 text-right font-mono text-xs font-medium text-neutral-900 dark:text-neutral-100">{formatCurrency(s.market_value, currency)}</td>
                  <td className={`py-2 px-3 text-right font-mono text-xs ${s.gain_loss >= 0 ? "text-neutral-900 dark:text-neutral-100" : "text-red-600"}`}>
                    {formatCurrency(s.gain_loss, currency)} ({formatPercent(s.gain_loss_pct)})
                  </td>
                  <td className="py-2 px-3">
                    <button onClick={async () => { if (token) { await investmentsApi.stocks.delete(token, s.id); load(); }}} className="text-neutral-300 hover:text-red-600 transition-colors">
                      <Trash2 size={13} />
                    </button>
                  </td>
                </tr>
              ))}
              {stocks.length === 0 && <tr><td colSpan={6} className="py-8 text-center text-xs text-neutral-400">No stocks yet</td></tr>}
            </tbody>
          </table>
        </div>
      </Card>

      {realEstate.length > 0 && (
        <Card>
          <CardTitle>Real Estate</CardTitle>
          <div className="mt-4 grid sm:grid-cols-2 gap-px bg-neutral-100 dark:bg-neutral-800">
            {realEstate.map(p => (
              <div key={p.id} className="bg-white dark:bg-neutral-900 p-4">
                <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">{p.name}</p>
                <p className="font-mono text-[10px] text-neutral-400 uppercase mt-0.5">{p.location} / {p.property_type}</p>
                <p className="font-mono text-lg font-bold mt-2 text-neutral-900 dark:text-neutral-100">{formatCurrency(p.estimated_value, currency)}</p>
                <p className="font-mono text-xs text-neutral-400">Rent: {formatCurrency(p.monthly_rent, currency)}/mo</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {business.length > 0 && (
        <Card>
          <CardTitle>Business Interests</CardTitle>
          <div className="mt-4 grid sm:grid-cols-2 gap-px bg-neutral-100 dark:bg-neutral-800">
            {business.map(b => (
              <div key={b.id} className="bg-white dark:bg-neutral-900 p-4">
                <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">{b.name}</p>
                <p className="font-mono text-[10px] text-neutral-400 uppercase mt-0.5">{b.equity_percent}% equity</p>
                <p className="font-mono text-lg font-bold mt-2 text-neutral-900 dark:text-neutral-100">{formatCurrency(b.current_value, currency)}</p>
                <p className={`font-mono text-xs ${b.gain_loss >= 0 ? "text-neutral-500" : "text-red-600"}`}>
                  G/L: {formatCurrency(b.gain_loss, currency)}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Modal open={showStockModal} onClose={() => setShowStockModal(false)} title="Add Stock">
        <form onSubmit={addStock} className="space-y-4">
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Ticker</label>
            <Input placeholder="e.g. AAPL" value={stockForm.ticker} onChange={e => setStockForm({...stockForm, ticker: e.target.value})} required />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Company</label>
            <Input placeholder="Company name" value={stockForm.name} onChange={e => setStockForm({...stockForm, name: e.target.value})} required />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Shares</label>
              <Input type="number" step="0.01" value={stockForm.shares || ""} onChange={e => setStockForm({...stockForm, shares: parseFloat(e.target.value) || 0})} required />
            </div>
            <div>
              <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Avg Cost</label>
              <Input type="number" step="0.01" value={stockForm.avg_cost || ""} onChange={e => setStockForm({...stockForm, avg_cost: parseFloat(e.target.value) || 0})} required />
            </div>
            <div>
              <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Price</label>
              <Input type="number" step="0.01" value={stockForm.current_price || ""} onChange={e => setStockForm({...stockForm, current_price: parseFloat(e.target.value) || 0})} required />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Sector</label>
            <Input placeholder="Optional" value={stockForm.sector} onChange={e => setStockForm({...stockForm, sector: e.target.value})} />
          </div>
          <Button type="submit" className="w-full">Add Stock</Button>
        </form>
      </Modal>
    </div>
  );
}
