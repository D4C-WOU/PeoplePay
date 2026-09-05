"use client";

import { useId, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  Check,
  Clock4,
  Eye,
  EyeOff,
  Loader2,
  ShieldCheck,
  Users2,
  Wallet,
} from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { ApiError } from "@/lib/api";

const FEATURES = [
  {
    icon: Users2,
    title: "Employee management",
    desc: "Profiles, contracts, and org structure in one connected view.",
  },
  {
    icon: Clock4,
    title: "Attendance & leave",
    desc: "Schedules, check-ins, and leave balances tracked automatically.",
  },
  {
    icon: Wallet,
    title: "Payroll engine",
    desc: "Rule-based salary computation with audit-ready payslips.",
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
  const emailId = useId();
  const passwordId = useId();

  const [email, setEmail] = useState("admin@peoplepay.com");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (loading) return;

    setLoading(true);
    setError(null);

    try {
      await login({ email: email.trim(), password });
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Invalid credentials");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-brand-panel" aria-label="PeoplePay360 overview">
        <div className="login-brand-grid" aria-hidden="true" />

        <div className="login-brand-content">
          <div className="login-brand-mark">
            <span>P3</span>
          </div>

          <div className="login-brand-copy">
            <p className="login-kicker">PeoplePay360</p>
            <h1>
              HR &amp; payroll,
              <br />
              without the busywork.
            </h1>
            <p className="login-brand-description">
              One connected workspace for employee records, attendance, leave,
              and payroll processing—with the detail and control your team
              needs.
            </p>
          </div>

          <div className="login-feature-list">
            {FEATURES.map(({ icon: Icon, title, desc }) => (
              <div className="login-feature" key={title}>
                <div className="login-feature-icon" aria-hidden="true">
                  <Icon size={18} strokeWidth={1.8} />
                </div>
                <div>
                  <h2>{title}</h2>
                  <p>{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="login-security">
          <ShieldCheck size={15} />
          <span>Secure workspace access</span>
          <span className="login-security-dot" aria-hidden="true" />
          <span>© {new Date().getFullYear()} PeoplePay360</span>
        </div>
      </section>

      <section className="login-form-panel">
        <div className="login-form-wrap">
          <div className="login-mobile-brand">
            <div className="login-mobile-mark">P3</div>
            <span>PeoplePay360</span>
          </div>

          <div className="login-heading">
            <div className="login-heading-badge">
              <span className="login-status-dot" />
              Workspace sign in
            </div>
            <h2>Welcome back</h2>
            <p>Sign in to continue to your PeoplePay360 workspace.</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit} noValidate>
            <div className="login-field">
              <label htmlFor={emailId}>Work email</label>
              <input
                id={emailId}
                name="email"
                type="email"
                inputMode="email"
                autoComplete="username"
                autoCapitalize="none"
                spellCheck={false}
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@company.com"
                disabled={loading}
                aria-invalid={Boolean(error)}
                className="login-input"
              />
            </div>

            <div className="login-field">
              <div className="login-label-row">
                <label htmlFor={passwordId}>Password</label>
              </div>
              <div className="login-password-wrap">
                <input
                  id={passwordId}
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
                  disabled={loading}
                  aria-invalid={Boolean(error)}
                  className="login-input login-password-input"
                />
                <button
                  type="button"
                  className="login-password-toggle"
                  onClick={() => setShowPassword((visible) => !visible)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  aria-pressed={showPassword}
                  disabled={loading}
                >
                  {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="login-error" role="alert" aria-live="polite">
                <span className="login-error-icon">!</span>
                <div>
                  <strong>Sign in failed</strong>
                  <p>{error}</p>
                </div>
              </div>
            )}

            <button className="login-submit" type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="login-spinner" size={18} />
                  Signing you in…
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          <div className="login-demo">
            <div className="login-demo-header">
              <div>
                <p className="login-demo-title">Quick demo access</p>
                <p className="login-demo-subtitle">
                  Pick a role to prefill the email address.
                </p>
              </div>
              <span className="login-demo-count">{DEMO_ACCOUNTS.length}</span>
            </div>

            <div className="login-demo-list">
              {DEMO_ACCOUNTS.map((account) => {
                const active = email === account;
                return (
                  <button
                    key={account}
                    type="button"
                    className={`login-demo-account${active ? " is-active" : ""}`}
                    onClick={() => {
                      setEmail(account);
                      setError(null);
                    }}
                    disabled={loading}
                  >
                    <span className="login-demo-check" aria-hidden="true">
                      {active && <Check size={13} strokeWidth={2.5} />}
                    </span>
                    <span>{account}</span>
                  </button>
                );
              })}
            </div>

            <p className="login-demo-note">
              Demo passwords end with <strong>@123</strong>.
            </p>
          </div>

          <p className="login-form-footer">
            By signing in, you agree to use this workspace only with authorized
            credentials.
          </p>
        </div>
      </section>
    </main>
  );
}
