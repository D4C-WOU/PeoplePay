"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "@/lib/api";
import { clearToken, getToken, setToken } from "@/lib/auth";
import type { LoginPayload, TokenResponse, User } from "@/types/auth";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (payload: LoginPayload) => Promise<User>;
  logout: () => void;
  refresh: () => Promise<void>;
}

export const AuthContext = React.createContext<AuthContextValue | null>(null);

export function AppProviders({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = React.useState<User | null>(null);
  const [loading, setLoading] = React.useState(true);

  const refresh = React.useCallback(async () => {
    const token = getToken();
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await apiRequest<User>("/auth/me");
      setUser(me);
    } catch {
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    const timeout = window.setTimeout(() => {
      void refresh();
    }, 0);
    return () => window.clearTimeout(timeout);
  }, [refresh]);

  React.useEffect(() => {
    const handleSessionExpired = () => {
      setUser(null);
      router.replace("/login");
    };
    window.addEventListener("peoplepay:session-expired", handleSessionExpired);
    return () =>
      window.removeEventListener("peoplepay:session-expired", handleSessionExpired);
  }, [router]);

  const login = React.useCallback(async (payload: LoginPayload) => {
    const res = await apiRequest<TokenResponse>("/auth/login", {
      method: "POST",
      body: payload,
    });
    setToken(res.access_token);
    const me = await apiRequest<User>("/auth/me");
    setUser(me);
    return me;
  }, []);

  const logout = React.useCallback(() => {
    clearToken();
    setUser(null);
    router.replace("/login");
  }, [router]);

  const value = React.useMemo(
    () => ({ user, loading, login, logout, refresh }),
    [user, loading, login, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
