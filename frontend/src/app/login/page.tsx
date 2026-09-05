"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Users2,
  Clock4,
  Wallet,
  ShieldCheck,
  ArrowRight,
  Loader2,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { ApiError } from "@/lib/api";

const FEATURES = [
  {
    icon: Users2,
    title: "Employee management",
    desc: "Profiles, contracts, and org structure in one connected view",
  },
  {
    icon: Clock4,
    title: "Attendance & leave",
    desc: "Schedules, check-ins, and leave balances tracked automatically",
  },
  {
    icon: Wallet,
    title: "Payroll engine",
    desc: "Rule-based salary computation with audit-ready payslips",
  },
];

const DEMO_ACCOUNTS = [
  "admin@peoplepay.com",
  "hr@peoplepay.com",
  "payroll.manager@peoplepay.com",
  "employee@peoplepay.com",
];

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("admin@peoplepay.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login({ email, password });
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Invalid credentials");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen bg-[var(--pp-page-bg)]">
      <div
        className="relative hidden w-[480px] flex-col justify-between overflow-hidden p-11 lg:flex"
        style={{
          background:
            "radial-gradient(1200px 600px at -10% -10%, #312e81 0%, transparent 55%), radial-gradient(900px 500px at 110% 110%, #9a3412 0%, transparent 50%), var(--pp-sidebar-bg)",
        }}
      >
        <div className="pointer-events-none absolute inset-0 opacity-[0.06] [background-image:linear-gradient(#fff_1px,transparent_1px),linear-gradient(90deg,#fff_1px,transparent_1px)] [background-size:36px_36px]" />

        <div className="relative z-10">
          <div className="mb-14 flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-2xl bg-white/10 text-sm font-bold text-white ring-1 ring-white/15">
              P3
            </div>
            <span className="text-base font-semibold tracking-tight text-white">
              PeoplePay360
            </span>
          </div>

          <h1 className="mb-4 text-[2.2rem] font-semibold leading-[1.15] tracking-tight text-white">
            HR &amp; Payroll,
            <br />
            reimagined.
          </h1>
          <p className="mb-11 max-w-sm text-sm leading-relaxed text-white/55">
            One connected platform for employee records, attendance, leave, and
            payroll processing — with a full audit trail.
          </p>

          <div className="space-y-5">
            {FEATURES.map((f) => (
              <div key={f.title} className="flex gap-3.5">
                <div className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-white/8 ring-1 ring-white/10">
                  <f.icon className="size-4 text-white/80" />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{f.title}</p>
                  <p className="mt-0.5 text-xs leading-relaxed text-white/45">
                    {f.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 flex items-center gap-2 text-xs text-white/35">
          <ShieldCheck className="size-3.5" />© {new Date().getFullYear()}{" "}
          PeoplePay360 · Enterprise-grade security
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center px-6 py-10">
        <div className="w-full max-w-sm">
          <div className="mb-8">
            <div className="mb-6 flex items-center gap-2 lg:hidden">
              <div className="flex size-8 items-center justify-center rounded-xl bg-[var(--pp-brand)] text-sm font-bold text-white">
                P3
              </div>
              <span className="font-semibold text-slate-900">PeoplePay360</span>
            </div>
            <h2 className="text-xl font-semibold tracking-tight text-slate-900">
              Welcome back
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Sign in with your workspace credentials
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-[var(--pp-border-strong)] bg-white px-3.5 py-2.5 text-sm shadow-[var(--pp-shadow-xs)] outline-none transition focus:border-[var(--pp-brand)] focus:ring-4 focus:ring-[var(--pp-brand-light)]"
                placeholder="you@company.com"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-[var(--pp-border-strong)] bg-white px-3.5 py-2.5 text-sm shadow-[var(--pp-shadow-xs)] outline-none transition focus:border-[var(--pp-brand)] focus:ring-4 focus:ring-[var(--pp-brand-light)]"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="rounded-xl border border-[var(--pp-danger)]/25 bg-[var(--pp-danger-bg)] px-3.5 py-2.5 text-sm text-[var(--pp-danger)]">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--pp-brand)] py-2.5 text-sm font-medium text-white shadow-[var(--pp-shadow-sm)] transition hover:bg-[var(--pp-brand-dark)] disabled:opacity-60"
            >
              {loading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <>
                  Sign in <ArrowRight className="size-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 rounded-2xl border border-[var(--pp-border)] bg-[var(--pp-brand-light)]/60 p-3.5">
            <p className="mb-1 text-xs font-semibold text-slate-700">
              Demo accounts
            </p>
            <div className="flex flex-wrap gap-1.5">
              {DEMO_ACCOUNTS.map((acc) => (
                <button
                  key={acc}
                  type="button"
                  onClick={() => setEmail(acc)}
                  className="rounded-lg border border-[var(--pp-border-strong)] bg-white px-2 py-1 text-[11px] text-slate-600 hover:border-[var(--pp-brand)] hover:text-[var(--pp-brand)]"
                >
                  {acc}
                </button>
              ))}
            </div>
            <p className="mt-2 text-[11px] text-slate-400">
              All passwords end with @123
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
