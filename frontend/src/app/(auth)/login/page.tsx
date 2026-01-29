"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-950 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-10">
          <h1 className="font-mono text-sm font-bold tracking-widest text-neutral-900 dark:text-neutral-100">ASSETFLOW</h1>
          <div className="mt-1 h-0.5 w-6 bg-accent" />
          <p className="text-xs text-neutral-400 mt-4 uppercase tracking-wider">Sign in to your account</p>
        </div>
        <form onSubmit={handleSubmit} className="border border-neutral-200 bg-white dark:bg-neutral-900 dark:border-neutral-800 p-8 space-y-5">
          {error && <p className="text-xs text-red-600 border border-red-200 bg-red-50 dark:bg-red-950/30 dark:border-red-900 p-3">{error}</p>}
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Email</label>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="you@example.com" />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-500 mb-2">Password</label>
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="••••••••" />
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </Button>
          <p className="text-center text-xs text-neutral-400">
            No account?{" "}
            <Link href="/register" className="text-neutral-900 dark:text-neutral-100 hover:underline">Register</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
