"use client";

import Link from "next/link";
import {
  ArrowRight,
  Calculator,
  CircleDollarSign,
  PlayCircle,
  Receipt,
  ReceiptText,
  Users,
} from "lucide-react";

import { Header } from "@/components/layout/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/status-badge";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { EmptyState } from "@/components/shared/empty-state";
import { usePayruns } from "@/hooks/usePayroll";

function money(value: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

function periodDate(value: string) {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function payrollTitle(value: string) {
  return `${new Intl.DateTimeFormat("en-IN", {
    month: "long",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`))} Payroll`;
}

export default function PayrollOverviewPage() {
  const { data: payruns, loading, error } = usePayruns();
  const recent = (payruns ?? []).slice(0, 5);
  const latest = [...(payruns ?? [])].sort((left, right) =>
    right.period_start.localeCompare(left.period_start),
  )[0];

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Payroll"
        description="Run payroll, review payslips, and manage the payroll lifecycle."
      />
      <div className="flex-1 p-4 sm:p-6">
        <div className="mx-auto w-full max-w-370 space-y-6">
          {latest && (
            <Card className="overflow-hidden border-(--pp-border-strong) shadow-(--pp-shadow-sm)">
              <CardHeader className="border-b border-(--pp-border) bg-(--pp-brand-light) px-5 py-5 sm:px-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.14em] text-(--pp-brand)">
                      Payroll dashboard
                    </p>
                    <CardTitle className="mt-1 text-xl">
                      {payrollTitle(latest.period_start)}
                    </CardTitle>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {periodDate(latest.period_start)}
                      <span className="mx-2" aria-hidden="true">
                        →
                      </span>
                      {periodDate(latest.period_end)}
                    </p>
                  </div>
                  <StatusBadge status={latest.status} />
                </div>
              </CardHeader>
              <CardContent className="grid grid-cols-2 divide-x divide-y divide-(--pp-border) p-0 lg:grid-cols-5 lg:divide-y-0">
                <div className="p-5 lg:p-6">
                  <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                    <Users className="size-4 text-(--pp-brand)" /> Employees
                  </p>
                  <p className="mt-3 text-2xl font-semibold text-slate-900">
                    {latest.employee_count}
                  </p>
                </div>
                <div className="p-5 lg:p-6">
                  <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                    <CircleDollarSign className="size-4 text-(--pp-brand)" />{" "}
                    Total gross
                  </p>
                  <p className="mt-3 text-xl font-semibold text-slate-900">
                    {money(Number(latest.total_gross))}
                  </p>
                </div>
                <div className="p-5 lg:p-6">
                  <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                    <ReceiptText className="size-4 text-(--pp-brand)" />{" "}
                    Deductions
                  </p>
                  <p className="mt-3 text-xl font-semibold text-slate-900">
                    {money(Number(latest.total_deductions))}
                  </p>
                </div>
                <div className="p-5 lg:p-6">
                  <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                    <Calculator className="size-4 text-(--pp-brand)" /> Total
                    tax
                  </p>
                  <p className="mt-3 text-xl font-semibold text-slate-900">
                    {money(Number(latest.total_tax))}
                  </p>
                </div>
                <div className="col-span-2 bg-(--pp-brand-light) p-5 lg:col-span-1 lg:p-6">
                  <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-(--pp-brand-dark)">
                    <CircleDollarSign className="size-4" /> Estimated net pay
                  </p>
                  <p className="mt-3 text-xl font-semibold text-(--pp-brand-dark)">
                    {money(Number(latest.total_net))}
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            <Card className="border-(--pp-border-strong) shadow-(--pp-shadow-xs)">
              <CardContent className="flex min-h-24 items-center justify-between gap-4 p-5">
                <div className="flex min-w-0 flex-1 items-center gap-3">
                  <div
                    className="flex size-11 shrink-0 items-center justify-center rounded-xl"
                    style={{ background: "var(--pp-brand-light)" }}
                  >
                    <PlayCircle
                      className="size-5"
                      style={{ color: "var(--pp-brand)" }}
                    />
                  </div>
                  <div className="min-w-0">
                    <p className="font-heading font-semibold text-slate-900">
                      Pay Runs
                    </p>
                    <p className="mt-0.5 text-sm text-muted-foreground">
                      Create, compute and finalize payroll periods
                    </p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  className="shrink-0"
                  nativeButton={false}
                  render={<Link href="/dashboard/payroll/payruns" />}
                >
                  Open <ArrowRight className="size-4" />
                </Button>
              </CardContent>
            </Card>
            <Card className="border-(--pp-border-strong) shadow-(--pp-shadow-xs)">
              <CardContent className="flex min-h-24 items-center justify-between gap-4 p-5">
                <div className="flex min-w-0 flex-1 items-center gap-3">
                  <div
                    className="flex size-11 shrink-0 items-center justify-center rounded-xl"
                    style={{ background: "var(--pp-brand-light)" }}
                  >
                    <Receipt
                      className="size-5"
                      style={{ color: "var(--pp-brand)" }}
                    />
                  </div>
                  <div className="min-w-0">
                    <p className="font-heading font-semibold text-slate-900">
                      Payslips
                    </p>
                    <p className="mt-0.5 text-sm text-muted-foreground">
                      Browse, download PDF, review breakdowns
                    </p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  className="shrink-0"
                  nativeButton={false}
                  render={<Link href="/dashboard/payroll/payslips" />}
                >
                  Open <ArrowRight className="size-4" />
                </Button>
              </CardContent>
            </Card>
          </div>

          <Card className="shadow-(--pp-shadow-xs)">
            <CardHeader className="border-b border-(--pp-border) px-5 py-4 sm:px-6">
              <CardTitle className="text-base">Recent pay runs</CardTitle>
              <p className="text-sm text-muted-foreground">
                The latest payroll periods and their current processing status.
              </p>
            </CardHeader>
            <CardContent className="p-4 sm:p-5">
              {error && <ErrorBanner message={error} />}
              {loading ? (
                <LoadingBanner label="Loading pay runs…" />
              ) : recent.length === 0 ? (
                <EmptyState
                  icon={PlayCircle}
                  title="No pay runs yet"
                  description="Start one from the Pay Runs page to begin processing payroll."
                />
              ) : (
                <div className="space-y-2">
                  {recent.map((run) => (
                    <Link
                      key={run.id}
                      href={`/dashboard/payroll/payruns/${run.id}`}
                      className="grid grid-cols-1 gap-3 rounded-xl border border-(--pp-border) p-4 text-sm transition-colors hover:border-(--pp-brand) hover:bg-(--pp-brand-light) sm:grid-cols-[minmax(0,1fr)_auto_auto] sm:items-center sm:gap-6"
                    >
                      <div className="min-w-0">
                        <p className="font-medium text-slate-900">
                          {periodDate(run.period_start)}
                          <span
                            className="mx-2 text-muted-foreground"
                            aria-hidden="true"
                          >
                            →
                          </span>
                          <span className="sr-only">to</span>
                          {periodDate(run.period_end)}
                        </p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          {run.employee_count} employees
                        </p>
                      </div>
                      <div className="flex items-center justify-between gap-4 sm:block sm:text-right">
                        <span className="text-xs text-muted-foreground sm:block">
                          Net payroll
                        </span>
                        <span className="font-medium text-slate-900 sm:block">
                          {money(Number(run.total_net))}
                        </span>
                      </div>
                      <div className="sm:justify-self-end">
                        <StatusBadge status={run.status} />
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
