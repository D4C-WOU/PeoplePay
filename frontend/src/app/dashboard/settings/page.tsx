"use client";

import { useState } from "react";
import {
  CheckCircle2,
  CircleUserRound,
  LogOut,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { API_BASE_URL } from "@/lib/api";
import { ROLE_LABELS } from "@/lib/auth";

export default function SettingsPage() {
  const { user, loading, refresh, logout } = useAuth();
  const [checking, setChecking] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  async function refreshAccount() {
    setChecking(true);
    setNotice(null);
    try {
      await refresh();
      setNotice("Account information refreshed from the server.");
    } catch {
      setNotice("We couldn't refresh your account. Please try again.");
    } finally {
      setChecking(false);
    }
  }

  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title="Settings"
        description="Manage your account and review workspace connection details."
      />
      <div className="pp-page-content mx-auto w-full max-w-5xl flex-1 space-y-5 p-4 sm:p-6">
        <section className="app-surface overflow-hidden">
          <div className="flex items-start gap-3 border-b border-[var(--pp-border)] p-5 sm:p-6">
            <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-[var(--pp-brand-light)] text-[var(--pp-brand)]">
              <CircleUserRound className="size-5" />
            </span>
            <div className="min-w-0 flex-1">
              <h2 className="text-base font-semibold text-[var(--text)]">
                Your account
              </h2>
              <p className="mt-1 text-sm text-[var(--text-2)]">
                Your identity and access role are managed by your PeoplePay360
                administrator.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshAccount}
              disabled={loading || checking}
            >
              <RefreshCw
                className={`size-4 ${checking ? "animate-spin" : ""}`}
              />
              Refresh
            </Button>
          </div>
          <div className="grid gap-5 p-5 sm:grid-cols-2 sm:p-6">
            <InfoField
              label="Username"
              value={user?.username ?? (loading ? "Loading…" : "Not available")}
            />
            <InfoField
              label="Email address"
              value={user?.email || "No email address on file"}
            />
            <InfoField
              label="Access role"
              value={user ? (ROLE_LABELS[user.role] ?? user.role) : "—"}
            />
            <div>
              <span className="text-xs font-medium uppercase tracking-wide text-[var(--text-3)]">
                Account status
              </span>
              <p className="mt-2 flex items-center gap-2 text-sm font-medium text-[var(--text)]">
                <span
                  className={`size-2 rounded-full ${user?.is_active !== false ? "bg-emerald-500" : "bg-amber-500"}`}
                />
                {loading
                  ? "Checking status…"
                  : user?.is_active
                    ? "Active"
                    : "Inactive or unavailable"}
              </p>
            </div>
          </div>
        </section>

        <section className="app-surface overflow-hidden">
          <div className="flex items-start gap-3 border-b border-[var(--pp-border)] p-5 sm:p-6">
            <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <ShieldCheck className="size-5" />
            </span>
            <div>
              <h2 className="text-base font-semibold text-[var(--text)]">
                Workspace connection
              </h2>
              <p className="mt-1 text-sm text-[var(--text-2)]">
                The frontend uses the configured Django API. Secrets and
                credentials are not displayed here.
              </p>
            </div>
          </div>
          <div className="space-y-4 p-5 sm:p-6">
            <div>
              <span className="text-xs font-medium uppercase tracking-wide text-[var(--text-3)]">
                API base URL
              </span>
              <p className="mt-1 break-all font-mono text-sm text-[var(--text)]">
                {API_BASE_URL}
              </p>
            </div>
            <div className="flex items-start gap-2 rounded-xl bg-[var(--pp-surface-muted)] p-3 text-sm text-[var(--text-2)]">
              <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-600" />
              <p>
                Account details are read from the authenticated backend session.
                Access permissions are enforced by the backend.
              </p>
            </div>
          </div>
        </section>

        <section className="app-surface flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
          <div>
            <h2 className="text-base font-semibold text-[var(--text)]">
              Sign out
            </h2>
            <p className="mt-1 text-sm text-[var(--text-2)]">
              End this browser session and return to the sign-in screen.
            </p>
          </div>
          <Button variant="destructive" onClick={logout}>
            <LogOut className="size-4" />
            Sign out
          </Button>
        </section>

        {notice && (
          <p role="status" className="text-sm text-[var(--text-2)]">
            {notice}
          </p>
        )}
      </div>
    </div>
  );
}

function InfoField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <span className="text-xs font-medium uppercase tracking-wide text-[var(--text-3)]">
        {label}
      </span>
      <p className="mt-2 break-words text-sm font-medium text-[var(--text)]">
        {value}
      </p>
    </div>
  );
}
