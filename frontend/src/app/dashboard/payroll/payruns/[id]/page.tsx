"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { AlertTriangle, Loader2, PlayCircle } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StatusBadge } from "@/components/shared/status-badge";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { usePayrun, usePayslips, payrunApi } from "@/hooks/usePayroll";
import { useEmployees } from "@/hooks/useEmployees";
import { ApiError } from "@/lib/api";
import type { PayrunValidation } from "@/types/payroll";

function money(value: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

function periodTitle(value: string) {
  return new Intl.DateTimeFormat("en-IN", {
    month: "long",
    year: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

export default function PayrunDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { data: payrun, loading, error, reload } = usePayrun(params.id);
  const {
    data: payslips,
    loading: payslipsLoading,
    reload: reloadPayslips,
  } = usePayslips({ payrun_id: params.id });
  const { data: employees } = useEmployees();

  const [busy, setBusy] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [validation, setValidation] = useState<PayrunValidation | null>(null);

  function refreshAll() {
    reload();
    reloadPayslips();
  }

  async function withAction(name: string, fn: () => Promise<void>) {
    setBusy(name);
    setActionError(null);
    try {
      await fn();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : `Could not ${name}.`,
      );
    } finally {
      setBusy(null);
    }
  }

  async function handleValidate() {
    if (!payrun) return;

    await withAction("validate", async () => {
      const result = await payrunApi.validate(payrun.id);
      setValidation(result);
    });
  }

  async function handleCompute() {
    if (!payrun) return;

    await withAction("compute payroll", async () => {
      await payrunApi.compute(payrun.id);
      refreshAll();
    });
  }

  if (loading) return <LoadingBanner label="Loading pay run…" />;
  if (error) return <ErrorBanner message={error} />;
  if (!payrun) return null;

  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title={`${periodTitle(payrun.period_start)} Payroll`}
        description={`${payrun.employee_count} employees selected`}
        actions={<StatusBadge status={payrun.status} />}
      />

      <div className="pp-page-content flex-1 space-y-4 p-4 sm:p-6">
        {actionError && <ErrorBanner message={actionError} />}

        <Card>
          <CardContent className="grid gap-4 p-5 sm:grid-cols-2 lg:grid-cols-5">
            <div>
              <p className="text-xs uppercase tracking-widest text-muted-foreground">Period</p>
              <p className="mt-1 font-medium">{payrun.period_start} → {payrun.period_end}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-widest text-muted-foreground">Payment date</p>
              <p className="mt-1 font-medium">{payrun.payment_date ?? "Not set"}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-widest text-muted-foreground">Salary structure</p>
              <p className="mt-1 font-medium">{payrun.salary_structure_name ?? "Not set"}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-widest text-muted-foreground">Employees</p>
              <p className="mt-1 font-medium">{payrun.employee_count}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-widest text-muted-foreground">Status</p>
              <div className="mt-1"><StatusBadge status={payrun.status} /></div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <Card>
            <CardContent className="pt-1">
              <p className="text-xs text-muted-foreground">Gross</p>
              <p className="text-lg font-semibold">{money(Number(payrun.total_gross))}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-1">
              <p className="text-xs text-muted-foreground">Deductions</p>
              <p className="text-lg font-semibold">{money(Number(payrun.total_deductions))}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-1">
              <p className="text-xs text-muted-foreground">Net</p>
              <p className="text-lg font-semibold">{money(Number(payrun.total_net))}</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-sm">Employees</CardTitle></CardHeader>
          <CardContent className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {(payrun.employee_ids ?? []).map((employeeId) => {
              const employee = employees?.find(
                (item) => String(item.id) === String(employeeId),
              );
              return (
                <div key={employeeId} className="rounded-lg border p-3 text-sm">
                  <p className="font-medium">
                    {employee ? `${employee.first_name} ${employee.last_name}` : employeeId}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {employee?.employee_number ?? "Employee"}
                  </p>
                </div>
              );
            })}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-sm">Payroll workflow</CardTitle></CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Button variant="outline" disabled={!!busy} onClick={handleValidate}>
              {busy === "validate" ? <Loader2 className="size-4 animate-spin" /> : <AlertTriangle />}
              Validate
            </Button>
            <Button disabled={!!busy || payrun.status !== "DRAFT"} onClick={handleCompute}>
              {busy === "compute payroll" ? <Loader2 className="size-4 animate-spin" /> : <PlayCircle />}
              Compute payroll
            </Button>
          </CardContent>
        </Card>

        {validation && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">
                Validation — {validation.valid ? "No issues" : `${validation.warnings.length} warning(s)`}
              </CardTitle>
            </CardHeader>
            {!validation.valid && (
              <CardContent className="space-y-2">
                {validation.warnings.map((warning, index) => (
                  <div key={index} className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
                    {typeof warning === "string" ? warning : warning.message ?? "Payroll warning"}
                  </div>
                ))}
              </CardContent>
            )}
          </Card>
        )}

        <Card>
          <CardHeader><CardTitle className="text-sm">Payslips</CardTitle></CardHeader>
          <CardContent>
            {payslipsLoading ? (
              <LoadingBanner label="Loading payslips…" />
            ) : !payslips || payslips.length === 0 ? (
              <p className="text-sm text-muted-foreground">No payslips yet — compute payroll to generate them.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead>Gross</TableHead>
                    <TableHead>Deductions</TableHead>
                    <TableHead>Net</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {payslips.map((slip) => (
                    <TableRow
                      key={slip.id}
                      className="cursor-pointer"
                      onClick={() => router.push(`/dashboard/payroll/payslips?payslip_id=${slip.id}`)}
                    >
                      <TableCell>
                        {slip.employee_name} <span className="text-xs text-muted-foreground">{slip.employee_number}</span>
                      </TableCell>
                      <TableCell>{money(Number(slip.gross_amount))}</TableCell>
                      <TableCell>{money(Number(slip.deductions_amount))}</TableCell>
                      <TableCell>{money(Number(slip.net_amount))}</TableCell>
                      <TableCell><StatusBadge status={slip.status} /></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
