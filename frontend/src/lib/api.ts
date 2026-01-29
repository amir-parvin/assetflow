const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  token?: string;
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, headers: customHeaders, ...rest } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((customHeaders as Record<string, string>) || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { headers, ...rest });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Auth
export const authApi = {
  register: (data: { email: string; password: string; full_name: string; currency?: string }) =>
    apiFetch("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    apiFetch<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  me: (token: string) => apiFetch<{ id: number; email: string; full_name: string; currency: string }>("/auth/me", { token }),
  updateMe: (token: string, data: { full_name?: string; currency?: string }) =>
    apiFetch<{ id: number; email: string; full_name: string; currency: string }>("/auth/me", {
      token, method: "PUT", body: JSON.stringify(data),
    }),
  refresh: (refresh_token: string) =>
    apiFetch<{ access_token: string; refresh_token: string }>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token }),
    }),
};

// Accounts
export const accountsApi = {
  list: (token: string) => apiFetch<any[]>("/accounts", { token }),
  purse: (token: string) => apiFetch<any[]>("/accounts/purse", { token }),
  create: (token: string, data: any) =>
    apiFetch("/accounts", { token, method: "POST", body: JSON.stringify(data) }),
  update: (token: string, id: number, data: any) =>
    apiFetch(`/accounts/${id}`, { token, method: "PUT", body: JSON.stringify(data) }),
  delete: (token: string, id: number) =>
    apiFetch(`/accounts/${id}`, { token, method: "DELETE" }),
};

// Transactions
export const transactionsApi = {
  list: (token: string, params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch<any[]>(`/transactions${qs}`, { token });
  },
  create: (token: string, data: any) =>
    apiFetch("/transactions", { token, method: "POST", body: JSON.stringify(data) }),
  update: (token: string, id: number, data: any) =>
    apiFetch(`/transactions/${id}`, { token, method: "PUT", body: JSON.stringify(data) }),
  delete: (token: string, id: number) =>
    apiFetch(`/transactions/${id}`, { token, method: "DELETE" }),
};

// Investments
export const investmentsApi = {
  stocks: {
    list: (token: string) => apiFetch<any[]>("/investments/stocks", { token }),
    create: (token: string, data: any) =>
      apiFetch("/investments/stocks", { token, method: "POST", body: JSON.stringify(data) }),
    update: (token: string, id: number, data: any) =>
      apiFetch(`/investments/stocks/${id}`, { token, method: "PUT", body: JSON.stringify(data) }),
    delete: (token: string, id: number) =>
      apiFetch(`/investments/stocks/${id}`, { token, method: "DELETE" }),
  },
  realEstate: {
    list: (token: string) => apiFetch<any[]>("/investments/real-estate", { token }),
    create: (token: string, data: any) =>
      apiFetch("/investments/real-estate", { token, method: "POST", body: JSON.stringify(data) }),
    delete: (token: string, id: number) =>
      apiFetch(`/investments/real-estate/${id}`, { token, method: "DELETE" }),
  },
  business: {
    list: (token: string) => apiFetch<any[]>("/investments/business", { token }),
    create: (token: string, data: any) =>
      apiFetch("/investments/business", { token, method: "POST", body: JSON.stringify(data) }),
    delete: (token: string, id: number) =>
      apiFetch(`/investments/business/${id}`, { token, method: "DELETE" }),
  },
  portfolio: (token: string) => apiFetch<any>("/investments/portfolio", { token }),
};

// Reports
export const reportsApi = {
  netWorth: (token: string) => apiFetch<any>("/reports/net-worth", { token }),
  balanceSheet: (token: string) => apiFetch<any>("/reports/balance-sheet", { token }),
  incomeExpense: (token: string, months?: number) =>
    apiFetch<any>(`/reports/income-expense${months ? `?months=${months}` : ""}`, { token }),
  cashFlow: (token: string, months?: number) =>
    apiFetch<any>(`/reports/cash-flow${months ? `?months=${months}` : ""}`, { token }),
  dashboard: (token: string) => apiFetch<any>("/reports/dashboard", { token }),
};

// Zakat
export const zakatApi = {
  calculate: (token: string, data: any) =>
    apiFetch<any>("/zakat/calculate", { token, method: "POST", body: JSON.stringify(data) }),
};
