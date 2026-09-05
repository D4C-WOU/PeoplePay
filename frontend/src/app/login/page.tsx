"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { ApiError } from "@/lib/api";

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
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div
        className="hidden lg:flex lg:w-[420px] flex-col justify-between p-10"
        style={{ background: "var(--pp-sidebar-bg)" }}
      >
        <div>
          <div className="flex items-center gap-3 mb-12">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center text-white font-bold text-sm"
              style={{ background: "var(--pp-brand)" }}
            >
              P3
            </div>
            <span className="text-white font-semibold text-base">
              PeoplePay360
            </span>
          </div>

          <h1 className="text-white text-3xl font-semibold leading-tight mb-4">
            HR & Payroll,
            <br />
            done right.
          </h1>
          <p className="text-gray-400 text-sm leading-relaxed mb-10">
            One platform for employee records, attendance, leave management, and
            payroll processing — with full audit history.
          </p>

          <div className="space-y-5">
            {[
              {
                icon: "👥",
                title: "Employee management",
                desc: "Profiles, contracts, and org structure in one view",
              },
              {
                icon: "🕐",
                title: "Attendance & leave",
                desc: "Schedules, check-ins, and leave balances tracked automatically",
              },
              {
                icon: "💰",
                title: "Payroll engine",
                desc: "Rule-based salary computation with PDF payslips",
              },
            ].map((f) => (
              <div key={f.title} className="flex gap-3">
                <span className="text-xl mt-0.5">{f.icon}</span>
                <div>
                  <p className="text-white text-sm font-medium">{f.title}</p>
                  <p className="text-gray-400 text-xs mt-0.5">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-gray-600 text-xs">
          © {new Date().getFullYear()} PeoplePay360
        </p>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center bg-white px-6">
        <div className="w-full max-w-sm">
          <div className="mb-8">
            <div className="lg:hidden flex items-center gap-2 mb-6">
              <div
                className="w-8 h-8 rounded flex items-center justify-center text-white font-bold text-sm"
                style={{ background: "var(--pp-brand)" }}
              >
                P3
              </div>
              <span className="font-semibold">PeoplePay360</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Sign in</h2>
            <p className="text-sm text-gray-500 mt-1">
              Use your workspace credentials
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5 uppercase tracking-wide">
                Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-gray-200 rounded-md px-3 py-2.5 text-sm focus:outline-none focus:border-purple-600 focus:ring-1 focus:ring-purple-600 transition"
                placeholder="you@company.com"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5 uppercase tracking-wide">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-200 rounded-md px-3 py-2.5 text-sm focus:outline-none focus:border-purple-600 focus:ring-1 focus:ring-purple-600 transition"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-md px-3 py-2">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-md text-sm font-medium text-white transition disabled:opacity-60"
              style={{ background: "var(--pp-brand)" }}
            >
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <div className="mt-6 p-3 bg-gray-50 rounded-md border border-gray-100">
            <p className="text-xs font-medium text-gray-700 mb-1">
              Demo accounts
            </p>
            <p className="text-xs text-gray-500 leading-relaxed">
              admin@peoplepay.com · hr@peoplepay.com
              <br />
              payroll.manager@peoplepay.com · employee@peoplepay.com
            </p>
            <p className="text-xs text-gray-400 mt-1">
              All passwords end with @123
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
