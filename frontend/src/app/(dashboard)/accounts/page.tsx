"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { accountsApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Modal } from "@/components/ui/modal";
import { formatCurrency } from "@/lib/utils";
import { Plus, Trash2 } from "lucide-react";

export default function AccountsPage() {
  const { token, user } = useAuth();
  const [purse, setPurse] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: "", type: "asset", category: "cash", balance: 0 });

  const currency = user?.currency || "USD";

  const load = () => { if (token) accountsApi.purse(token).then(setPurse).catch(console.error); };
  useEffect(load, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    await accountsApi.create(token, { ...form, currency });
    setForm({ name: "", type: "asset", category: "cash", balance: 0 });
    setShowModal(false);
    load();
  };

  const handleDelete = async (id: number) => {
    if (!token || !confirm("Delete this sub-segment?")) return;
    await accountsApi.delete(token, id);
    load();
  };

  const totalAssets = purse.filter(s => s.category !== "liability").reduce((sum, s) => sum + s.total_balance, 0);
  const totalLiabilities = purse.filter(s => s.category === "liability").reduce((sum, s) => sum + s.total_balance, 0);

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-mono text-xs tracking-widest text-accent uppercase mb-1">Your Purse</p>
          <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">Segments</h1>
        </div>
        <Button onClick={() => setShowModal(true)} size="sm">
          <Plus size={14} className="mr-1" /> Add
        </Button>
      </div>

      <div className="grid sm:grid-cols-3 gap-px bg-neutral-200 dark:bg-neutral-800">
        <div className="bg-white dark:bg-neutral-900 p-5">
          <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">Total Assets</p>
          <p className="mt-1 font-mono text-xl font-bold text-neutral-900 dark:text-neutral-100">{formatCurrency(totalAssets, currency)}</p>
        </div>
        <div className="bg-white dark:bg-neutral-900 p-5">
          <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">Total Liabilities</p>
          <p className="mt-1 font-mono text-xl font-bold text-red-600">{formatCurrency(totalLiabilities, currency)}</p>
        </div>
        <div className="bg-white dark:bg-neutral-900 p-5">
          <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">Net Worth</p>
          <p className="mt-1 font-mono text-xl font-bold text-neutral-900 dark:text-neutral-100">{formatCurrency(totalAssets - totalLiabilities, currency)}</p>
        </div>
      </div>

      {purse.map(segment => (
        <div key={segment.id}>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-accent font-mono text-xs">{"/"}{"/"}  </span>
            <h2 className="text-xs font-medium uppercase tracking-widest text-neutral-500">{segment.name}</h2>
            <span className="font-mono text-xs text-neutral-400">{formatCurrency(segment.total_balance, currency)}</span>
          </div>
          {segment.sub_segments.length === 0 ? (
            <p className="text-xs text-neutral-400 pl-6 py-2">No items in this segment</p>
          ) : (
            <div className="border border-neutral-200 dark:border-neutral-800 divide-y divide-neutral-100 dark:divide-neutral-800">
              {segment.sub_segments.map((a: any) => (
                <div key={a.id} className="flex items-center justify-between p-4 bg-white dark:bg-neutral-900 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 transition-colors">
                  <div>
                    <p className="text-sm text-neutral-900 dark:text-neutral-100">{a.name}</p>
                    <p className="font-mono text-[10px] text-neutral-400 uppercase mt-0.5">
                      {a.source_type ? `auto / ${a.source_type}` : a.category}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-sm font-medium text-neutral-900 dark:text-neutral-100">{formatCurrency(a.balance, a.currency)}</span>
                    {!a.source_type && (
                      <button onClick={() => handleDelete(a.id)} className="text-neutral-300 hover:text-red-600 transition-colors">
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}

      <Modal open={showModal} onClose={() => setShowModal(false)} title="Add Sub-Segment">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Name</label>
            <Input placeholder="e.g. Savings Account" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Type</label>
            <Select value={form.type} onChange={e => setForm({...form, type: e.target.value})}>
              <option value="asset">Asset</option>
              <option value="liability">Liability</option>
            </Select>
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Category</label>
            <Select value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
              {["cash","bank","investment","property","vehicle","equipment","crypto","loan","credit_card","mortgage","business","other","liability"].map(c => (
                <option key={c} value={c}>{c.replace("_", " ")}</option>
              ))}
            </Select>
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Balance</label>
            <Input type="number" step="0.01" placeholder="0.00" value={form.balance || ""} onChange={e => setForm({...form, balance: parseFloat(e.target.value) || 0})} />
          </div>
          <Button type="submit" className="w-full">Create</Button>
        </form>
      </Modal>
    </div>
  );
}
