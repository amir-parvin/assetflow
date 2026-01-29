"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { transactionsApi, accountsApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Modal } from "@/components/ui/modal";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Plus, Trash2 } from "lucide-react";

export default function TransactionsPage() {
  const { token, user } = useAuth();
  const [txns, setTxns] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [filter, setFilter] = useState({ type: "", category: "" });
  const [form, setForm] = useState({ account_id: 0, amount: 0, type: "expense", category: "", date: new Date().toISOString().split("T")[0], description: "" });

  const currency = user?.currency || "USD";

  const load = () => {
    if (!token) return;
    const params: Record<string, string> = {};
    if (filter.type) params.type = filter.type;
    if (filter.category) params.category = filter.category;
    transactionsApi.list(token, params).then(setTxns).catch(console.error);
    accountsApi.list(token).then(setAccounts).catch(console.error);
  };
  useEffect(load, [token, filter]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    await transactionsApi.create(token, form);
    setShowModal(false);
    load();
  };

  const handleDelete = async (id: number) => {
    if (!token || !confirm("Delete this transaction?")) return;
    await transactionsApi.delete(token, id);
    load();
  };

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-mono text-xs tracking-widest text-accent uppercase mb-1">Records</p>
          <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">Transactions</h1>
        </div>
        <Button onClick={() => { if (accounts.length > 0) setForm(f => ({...f, account_id: accounts[0].id})); setShowModal(true); }} size="sm">
          <Plus size={14} className="mr-1" /> Add
        </Button>
      </div>

      <div className="flex gap-3">
        <Select value={filter.type} onChange={e => setFilter({...filter, type: e.target.value})} className="w-36">
          <option value="">All types</option>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
          <option value="transfer">Transfer</option>
        </Select>
        <Input placeholder="Filter by category" value={filter.category} onChange={e => setFilter({...filter, category: e.target.value})} className="w-44" />
      </div>

      <div className="border border-neutral-200 dark:border-neutral-800 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-200 dark:border-neutral-800 text-left bg-neutral-50 dark:bg-neutral-900">
              <th className="py-3 px-4 text-xs font-medium uppercase tracking-wider text-neutral-400">Date</th>
              <th className="py-3 px-4 text-xs font-medium uppercase tracking-wider text-neutral-400">Description</th>
              <th className="py-3 px-4 text-xs font-medium uppercase tracking-wider text-neutral-400">Category</th>
              <th className="py-3 px-4 text-xs font-medium uppercase tracking-wider text-neutral-400">Type</th>
              <th className="py-3 px-4 text-xs font-medium uppercase tracking-wider text-neutral-400 text-right">Amount</th>
              <th className="py-3 px-4 w-8"></th>
            </tr>
          </thead>
          <tbody>
            {txns.map(t => (
              <tr key={t.id} className="border-b border-neutral-100 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 bg-white dark:bg-neutral-900">
                <td className="py-3 px-4 font-mono text-xs text-neutral-500">{formatDate(t.date)}</td>
                <td className="py-3 px-4 text-neutral-900 dark:text-neutral-100">{t.description || "-"}</td>
                <td className="py-3 px-4 text-xs uppercase tracking-wider text-neutral-400">{t.category}</td>
                <td className="py-3 px-4">
                  <span className={`text-xs font-medium uppercase tracking-wider ${t.type === "income" ? "text-neutral-900 dark:text-neutral-100" : t.type === "expense" ? "text-neutral-400" : "text-accent"}`}>
                    {t.type}
                  </span>
                </td>
                <td className={`py-3 px-4 text-right font-mono text-sm font-medium ${t.type === "income" ? "text-neutral-900 dark:text-neutral-100" : "text-neutral-400"}`}>
                  {t.type === "income" ? "+" : "-"}{formatCurrency(t.amount, currency)}
                </td>
                <td className="py-3 px-4">
                  <button onClick={() => handleDelete(t.id)} className="text-neutral-300 hover:text-red-600 transition-colors"><Trash2 size={13} /></button>
                </td>
              </tr>
            ))}
            {txns.length === 0 && (
              <tr><td colSpan={6} className="py-12 text-center text-xs text-neutral-400 bg-white dark:bg-neutral-900">No transactions yet</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <Modal open={showModal} onClose={() => setShowModal(false)} title="Add Transaction">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Account</label>
            <Select value={form.account_id} onChange={e => setForm({...form, account_id: parseInt(e.target.value)})}>
              {accounts.filter(a => !a.is_segment).map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
            </Select>
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Type</label>
            <Select value={form.type} onChange={e => setForm({...form, type: e.target.value})}>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
              <option value="transfer">Transfer</option>
            </Select>
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Category</label>
            <Input placeholder="e.g. salary, food, rent" value={form.category} onChange={e => setForm({...form, category: e.target.value})} required />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Amount</label>
            <Input type="number" step="0.01" placeholder="0.00" value={form.amount || ""} onChange={e => setForm({...form, amount: parseFloat(e.target.value) || 0})} required />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Date</label>
            <Input type="date" value={form.date} onChange={e => setForm({...form, date: e.target.value})} required />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Description</label>
            <Input placeholder="Optional" value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
          </div>
          <Button type="submit" className="w-full">Add Transaction</Button>
        </form>
      </Modal>
    </div>
  );
}
