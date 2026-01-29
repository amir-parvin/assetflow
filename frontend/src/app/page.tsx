import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-white dark:bg-neutral-950">
      <header className="flex items-center justify-between px-6 py-5 max-w-5xl mx-auto">
        <div>
          <span className="font-mono text-sm font-bold tracking-widest text-neutral-900 dark:text-neutral-100">ASSETFLOW</span>
          <div className="mt-0.5 h-0.5 w-6 bg-accent" />
        </div>
        <div className="flex gap-4 items-center">
          <Link href="/login" className="text-xs font-medium uppercase tracking-wider text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100 transition-colors">
            Login
          </Link>
          <Link href="/register" className="px-5 py-2.5 text-xs font-medium uppercase tracking-wider bg-neutral-900 text-white hover:bg-neutral-800 dark:bg-neutral-100 dark:text-neutral-900 dark:hover:bg-neutral-200 transition-colors">
            Get Started
          </Link>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6">
        <div className="py-24 md:py-32 max-w-2xl">
          <p className="font-mono text-xs tracking-widest text-accent uppercase mb-6">Personal Finance</p>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100 leading-[1.1]">
            Take control of your financial future.
          </h2>
          <p className="mt-6 text-neutral-500 leading-relaxed max-w-lg">
            Track assets, manage investments, monitor cash flow, and calculate zakat. One purse, clear segments, complete visibility.
          </p>
          <div className="mt-10 flex gap-4">
            <Link href="/register" className="px-8 py-3 bg-neutral-900 text-white text-xs font-medium uppercase tracking-wider hover:bg-neutral-800 dark:bg-neutral-100 dark:text-neutral-900 dark:hover:bg-neutral-200 transition-colors">
              Start Free
            </Link>
            <Link href="/login" className="px-8 py-3 border border-neutral-300 text-xs font-medium uppercase tracking-wider text-neutral-600 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-400 dark:hover:bg-neutral-900 transition-colors">
              Sign In
            </Link>
          </div>
        </div>

        <div className="border-t border-neutral-200 dark:border-neutral-800 py-16">
          <p className="font-mono text-xs tracking-widest text-neutral-400 uppercase mb-8">Features</p>
          <div className="grid md:grid-cols-3 gap-px bg-neutral-200 dark:bg-neutral-800">
            {[
              { title: "Net Worth", desc: "Complete financial picture with real-time asset and liability tracking." },
              { title: "Investments", desc: "Stocks, real estate, and business interests with gain/loss analysis." },
              { title: "Zakat", desc: "Accurate calculation based on gold/silver nisab with detailed breakdowns." },
              { title: "Cash Flow", desc: "Income and expenses with interactive charts and trend analysis." },
              { title: "One Purse", desc: "All accounts unified into segments and sub-segments. One view, full clarity." },
              { title: "Multi-Currency", desc: "Support for multiple currencies with user-level preferences." },
            ].map((f) => (
              <div key={f.title} className="bg-white dark:bg-neutral-950 p-6 group">
                <h3 className="text-xs font-medium uppercase tracking-widest text-neutral-900 dark:text-neutral-100 mb-2">
                  <span className="text-accent mr-2">{"/"}{"/"}  </span>{f.title}
                </h3>
                <p className="text-sm text-neutral-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>

      <footer className="py-8 text-center">
        <p className="font-mono text-[10px] tracking-widest text-neutral-300 dark:text-neutral-700 uppercase">
          AssetFlow &copy; {new Date().getFullYear()}
        </p>
      </footer>
    </div>
  );
}
