"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Wallet,
  ArrowLeftRight,
  BarChart3,
  TrendingUp,
  Calculator,
  Moon,
  Sun,
  LogOut,
  Settings,
} from "lucide-react";
import { useState, useEffect } from "react";

const navItems = [
  { href: "/dashboard", label: "DASHBOARD", icon: LayoutDashboard },
  { href: "/accounts", label: "PURSE", icon: Wallet },
  { href: "/transactions", label: "TRANSACTIONS", icon: ArrowLeftRight },
  { href: "/reports", label: "REPORTS", icon: BarChart3 },
  { href: "/investments", label: "INVESTMENTS", icon: TrendingUp },
  { href: "/zakat", label: "ZAKAT", icon: Calculator },
  { href: "/settings", label: "SETTINGS", icon: Settings },
];

interface SidebarProps {
  onLogout: () => void;
}

export function Sidebar({ onLogout }: SidebarProps) {
  const pathname = usePathname();
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("theme");
    if (stored === "dark" || (!stored && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      setDark(true);
      document.documentElement.classList.add("dark");
    }
  }, []);

  const toggleDark = () => {
    setDark(!dark);
    document.documentElement.classList.toggle("dark");
    localStorage.setItem("theme", !dark ? "dark" : "light");
  };

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex md:w-56 md:flex-col md:fixed md:inset-y-0 bg-white dark:bg-neutral-950 border-r border-neutral-200 dark:border-neutral-800">
        <div className="flex-1 flex flex-col min-h-0">
          <div className="px-5 py-6 border-b border-neutral-200 dark:border-neutral-800">
            <h1 className="font-mono text-sm font-bold tracking-widest text-neutral-900 dark:text-neutral-100">ASSETFLOW</h1>
            <div className="mt-1 h-0.5 w-6 bg-accent" />
          </div>
          <nav className="flex-1 px-3 py-4 space-y-0.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 text-xs font-medium tracking-wider transition-colors",
                    active
                      ? "bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900"
                      : "text-neutral-500 hover:text-neutral-900 hover:bg-neutral-50 dark:hover:text-neutral-100 dark:hover:bg-neutral-900"
                  )}
                >
                  <Icon size={15} strokeWidth={1.5} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="px-3 py-4 border-t border-neutral-200 dark:border-neutral-800 space-y-0.5">
            <button
              onClick={toggleDark}
              className="flex items-center gap-3 px-3 py-2.5 text-xs font-medium tracking-wider text-neutral-500 hover:text-neutral-900 hover:bg-neutral-50 dark:hover:text-neutral-100 dark:hover:bg-neutral-900 w-full"
            >
              {dark ? <Sun size={15} strokeWidth={1.5} /> : <Moon size={15} strokeWidth={1.5} />}
              {dark ? "LIGHT" : "DARK"}
            </button>
            <button
              onClick={onLogout}
              className="flex items-center gap-3 px-3 py-2.5 text-xs font-medium tracking-wider text-neutral-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/50 w-full"
            >
              <LogOut size={15} strokeWidth={1.5} />
              LOGOUT
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-white dark:bg-neutral-950 border-t border-neutral-200 dark:border-neutral-800 flex justify-around py-2">
        {navItems.slice(0, 5).map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-col items-center gap-0.5 px-2 py-1 text-[10px] tracking-wider",
                active ? "text-neutral-900 dark:text-neutral-100" : "text-neutral-400"
              )}
            >
              <Icon size={18} strokeWidth={1.5} />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </>
  );
}
