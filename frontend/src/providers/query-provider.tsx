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

  const refresh = React.useCallback(async () => {
    const token = getToken();

    /*
     * If there is no access token, there is no existing session
     * to restore.
     */
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      /*
       * Ask Django for the current authenticated user instead of
       * trusting information stored in the browser.
       *
       * The backend remains the source of truth for:
       * - user identity
       * - role
       * - account status
       */
      const me = await apiRequest<User>("/auth/me/");

      setUser(me);
    } catch {
      /*
       * If the existing session cannot be restored, remove the
       * local authentication state.
       */
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    /*
     * Session restoration is an asynchronous operation.
     *
     * Scheduling it after the current effect finishes avoids the
     * React 19 set-state-in-effect lint warning while preserving
     * the same application behavior.
     */
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [refresh]);

  React.useEffect(() => {
    /*
     * apiRequest() emits this event whenever the backend reports
     * that the current authentication session is no longer valid.
     *
     * This listener keeps the UI synchronized with that event.
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

  const login = React.useCallback(async (payload: LoginPayload) => {
    /*
     * Django SimpleJWT returns both:
     *
     * access  -> short-lived token used for API requests
     * refresh -> longer-lived token used to obtain a new access token
     */
    const response = await apiRequest<TokenResponse>("/auth/login/", {
      method: "POST",
      body: payload,
    });

    /*
     * Store both tokens so the authentication layer has the
     * information required for the current JWT session.
     */
    setToken(response.access);
    setRefreshToken(response.refresh);

    /*
     * Fetch the authenticated user's actual backend profile.
     *
     * This prevents the frontend from having to infer the user's
     * role from the login form or token payload.
     */
    const me = await apiRequest<User>("/auth/me/");

    setUser(me);

    return me;
  }, []);

  const logout = React.useCallback(() => {
    /*
     * JWT authentication is stateless on the backend.
     *
     * Removing the locally stored tokens ends this browser session.
     */
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
