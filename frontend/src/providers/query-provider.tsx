"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { apiRequest } from "@/lib/api";

import { clearToken, getToken, setRefreshToken, setToken } from "@/lib/auth";

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

  /**
   * Restore an existing login session when the application starts.
   */
  const refresh = React.useCallback(async () => {
    const token = getToken();

    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      /*
       * Django remains the source of truth for the current user.
       */
      const me = await apiRequest<User>("/auth/me/");

      setUser(me);
    } catch {
      /*
       * If the access token and refresh token are both invalid,
       * remove the local session.
       */
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    /*
     * Delay session restoration until after the initial effect.
     *
     * This avoids unnecessary React 19 effect/lint warnings while
     * keeping authentication initialization asynchronous.
     */
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [refresh]);

  React.useEffect(() => {
    /**
     * The API layer emits this event when a JWT session can no
     * longer be recovered.
     */
    const handleSessionExpired = () => {
      setUser(null);
      router.replace("/login");
    };

    window.addEventListener("peoplepay:session-expired", handleSessionExpired);

    return () => {
      window.removeEventListener(
        "peoplepay:session-expired",
        handleSessionExpired,
      );
    };
  }, [router]);

  /**
   * Authenticate against Django SimpleJWT.
   */
  const login = React.useCallback(async (payload: LoginPayload) => {
    /*
     * Django's default AbstractUser authentication uses:
     *
     * username + password
     */
    const response = await apiRequest<TokenResponse>("/auth/login/", {
      method: "POST",
      body: payload,
    });

    /*
     * Store both JWT tokens.
     */
    setToken(response.access);
    setRefreshToken(response.refresh);

    /*
     * Fetch the actual authenticated user.
     *
     * This gives us the backend-controlled role and profile.
     */
    const me = await apiRequest<User>("/auth/me/");

    setUser(me);

    return me;
  }, []);

  /**
   * End the browser's current JWT session.
   */
  const logout = React.useCallback(() => {
    clearToken();
    setUser(null);

    router.replace("/login");
  }, [router]);

  const value = React.useMemo(
    () => ({
      user,
      loading,
      login,
      logout,
      refresh,
    }),
    [user, loading, login, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
