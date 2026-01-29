"use client";
import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

const CURRENCIES = ["USD", "EUR", "GBP", "BDT", "SAR", "AED", "MYR", "SGD", "CAD", "AUD", "INR", "PKR", "TRY", "EGP", "KWD", "QAR", "BHD", "OMR", "JOD"];

export default function SettingsPage() {
  const { user, updateUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [currency, setCurrency] = useState(user?.currency || "USD");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await updateUser({ full_name: fullName, currency });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8 max-w-lg">
      <div>
        <p className="font-mono text-xs tracking-widest text-accent uppercase mb-1">Preferences</p>
        <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">Settings</h1>
      </div>

      <Card>
        <CardTitle>Profile</CardTitle>
        <div className="mt-4 space-y-5">
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Email</label>
            <p className="font-mono text-sm text-neutral-400">{user?.email}</p>
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Full Name</label>
            <Input value={fullName} onChange={e => setFullName(e.target.value)} />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Currency</label>
            <Select value={currency} onChange={e => setCurrency(e.target.value)}>
              {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
            </Select>
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={handleSave} disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </Button>
            {saved && <span className="text-xs text-accent font-mono">Saved</span>}
          </div>
        </div>
      </Card>
    </div>
  );
}
