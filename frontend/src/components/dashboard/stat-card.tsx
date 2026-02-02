import { cn } from "@/lib/utils";
import { formatCurrency } from "@/lib/utils";
import { LucideIcon, Pencil } from "lucide-react";

interface StatCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  trend?: "up" | "down";
  currency?: string;
  onEdit?: () => void;
  suffix?: string;
}

export function StatCard({ title, value, icon: Icon, trend, currency = "USD", onEdit, suffix }: StatCardProps) {
  return (
    <div className="border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-widest text-neutral-400">{title}</p>
          <p className={cn(
            "mt-2 font-mono text-2xl font-bold tracking-tight",
            trend === "down" ? "text-red-600" : "text-neutral-900 dark:text-neutral-100"
          )}>
            {suffix ? `${value}${suffix}` : formatCurrency(value, currency)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {onEdit && (
            <button
              onClick={onEdit}
              className="text-neutral-300 hover:text-accent transition-colors dark:text-neutral-700 dark:hover:text-accent"
            >
              <Pencil size={14} strokeWidth={1.5} />
            </button>
          )}
          <div className="text-neutral-300 dark:text-neutral-700">
            <Icon size={20} strokeWidth={1.5} />
          </div>
        </div>
      </div>
    </div>
  );
}
