"use client";
import { useState, useEffect, useCallback } from "react";
import { authApi } from "@/lib/api";

interface User {
  id: number;
  email: string;
  full_name: string;
  currency: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("token");
    if (stored) {
      setToken(stored);
      authApi.me(stored).then(setUser).catch(() => {
        localStorage.removeItem("token");
        localStorage.removeItem("refresh_token");
      }).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await authApi.login({ email, password });
    localStorage.setItem("token", res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    setToken(res.access_token);
    const me = await authApi.me(res.access_token);
    setUser(me);
  }, []);

  const register = useCallback(async (email: string, password: string, full_name: string, currency?: string) => {
    await authApi.register({ email, password, full_name, currency });
    await login(email, password);
  }, [login]);

  const updateUser = useCallback(async (data: { full_name?: string; currency?: string }) => {
    if (!token) return;
    const updated = await authApi.updateMe(token, data);
    setUser(updated);
  }, [token]);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    setToken(null);
    setUser(null);
  }, []);

  return { user, token, loading, login, register, logout, updateUser };
}
