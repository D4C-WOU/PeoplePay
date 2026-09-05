"use client";

import Link from "next/link";
import { PlayCircle, Receipt, ArrowRight } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/status-badge";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { usePayruns } from "@/hooks/usePayroll";

function money(value: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

export default function PayrollOverviewPage() {
  const { data: payruns, loading, error } = usePayruns();
  const recent = (payruns ?? []).slice(0, 5);

  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title="Payroll"
        description="Run payroll, review payslips, and manage the payroll lifecycle."
      />
      <div className="pp-page-content flex-1 space-y-4 p-4 sm:p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Card>
            <CardContent className="flex items-center justify-between pt-1">
              <div className="flex items-center gap-3">
                <div
                  className="flex size-10 items-center justify-center rounded-lg"
                  style={{ background: "var(--pp-brand-light)" }}
                >
                  <PlayCircle
                    className="size-5"
                    style={{ color: "var(--pp-brand)" }}
                  />
                </div>
                <div>
                  <p className="font-medium">Pay Runs</p>
                  <p className="text-xs text-muted-foreground">
                    Create, compute and finalize payroll periods
                  </p>
                </div>
              </div>
              <Button
                variant="outline"
                render={<Link href="/dashboard/payroll/payruns" />}
              >
                Open <ArrowRight />
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center justify-between pt-1">
              <div className="flex items-center gap-3">
                <div
                  className="flex size-10 items-center justify-center rounded-lg"
                  style={{ background: "var(--pp-brand-light)" }}
                >
                  <Receipt
                    className="size-5"
                    style={{ color: "var(--pp-brand)" }}
                  />
                </div>
                <div>
                  <p className="font-medium">Payslips</p>
                  <p className="text-xs text-muted-foreground">
                    Browse, download PDF, review breakdowns
                  </p>
                </div>
              </div>
              <Button
                variant="outline"
                render={<Link href="/dashboard/payroll/payslips" />}
              >
                Open <ArrowRight />
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Recent pay runs</CardTitle>
          </CardHeader>
          <CardContent>
            {error && <ErrorBanner message={error} />}
            {loading ? (
              <LoadingBanner label="Loading pay runs…" />
            ) : recent.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No pay runs yet. Start one from the Pay Runs page.
              </p>
            ) : (
              <div className="space-y-2">
                {recent.map((run) => (
                  <Link
                    key={run.id}
                    href={`/dashboard/payroll/payruns/${run.id}`}
                    className="flex items-center justify-between rounded-lg border p-3 text-sm transition-colors hover:bg-muted/50"
                  >
                    <div>
                      <p className="font-medium">
                        {run.period_start} → {run.period_end}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {run.employee_count} employees
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm">
                        {money(Number(run.total_net))}
                      </span>
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
  );
}
