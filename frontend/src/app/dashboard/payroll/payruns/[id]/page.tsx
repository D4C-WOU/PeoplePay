"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import {
  AlertTriangle,
  Ban,
  CheckCircle2,
  Loader2,
  Mail,
  PlayCircle,
} from "lucide-react";

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
import { ApiError } from "@/lib/api";
import type { PayrunValidation } from "@/types/payroll";

function money(value: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value ?? 0);
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

  const [busy, setBusy] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [validation, setValidation] = useState<PayrunValidation | null>(null);
  const [sendResult, setSendResult] = useState<{
    total: number;
    sent: number;
    failed: number;
  } | null>(null);

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

  async function handleProcess() {
    if (!payrun) return;
    await withAction("compute payroll", async () => {
      await payrunApi.process(payrun.id);
      refreshAll();
    });
  }

  async function handleFinalize() {
    if (!payrun) return;
    await withAction("finalize", async () => {
      await payrunApi.finalize(payrun.id);
      refreshAll();
    });
  }

  async function handleCancel() {
    if (!payrun) return;
    await withAction("cancel", async () => {
      await payrunApi.cancel(payrun.id);
      refreshAll();
    });
  }

  async function handleSend() {
    if (!payrun) return;
    await withAction("send payslips", async () => {
      const result = await payrunApi.sendPayslips(payrun.id);
      setSendResult(result);
    });
  }

  if (loading) return <LoadingBanner label="Loading pay run…" />;
  if (error) return <ErrorBanner message={error} />;
  if (!payrun) return null;

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title={`${payrun.period_start} → ${payrun.period_end}`}
        description={`${payrun.employee_count} employees selected`}
        actions={<StatusBadge status={payrun.status} />}
      />
      <div className="flex-1 space-y-4 p-4 sm:p-6">
        {actionError && <ErrorBanner message={actionError} />}

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Card>
            <CardContent className="pt-1">
              <p className="text-xs text-muted-foreground">Gross</p>
              <p className="text-lg font-semibold">
                {money(Number(payrun.total_gross))}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-1">
              <p className="text-xs text-muted-foreground">Deductions</p>
              <p className="text-lg font-semibold">
                {money(Number(payrun.total_deductions))}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-1">
              <p className="text-xs text-muted-foreground">Tax</p>
              <p className="text-lg font-semibold">
                {money(Number(payrun.total_tax))}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-1">
              <p className="text-xs text-muted-foreground">Net</p>
              <p className="text-lg font-semibold">
                {money(Number(payrun.total_net))}
              </p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Workflow actions</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              disabled={!!busy}
              onClick={handleValidate}
            >
              {busy === "validate" ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <AlertTriangle />
              )}
              Validate
            </Button>
            <Button
              disabled={!!busy || payrun.status !== "DRAFT"}
              onClick={handleProcess}
            >
              {busy === "compute payroll" ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <PlayCircle />
              )}
              Compute payroll
            </Button>
            <Button
              disabled={!!busy || payrun.status !== "PROCESSING"}
              onClick={handleFinalize}
            >
              {busy === "finalize" ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <CheckCircle2 />
              )}
              Finalize
            </Button>
            <Button
              variant="outline"
              disabled={!!busy || payrun.status !== "COMPLETED"}
              onClick={handleSend}
            >
              {busy === "send payslips" ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Mail />
              )}
              Send payslips
            </Button>
            <Button
              variant="destructive"
              disabled={
                !!busy || !["DRAFT", "PROCESSING"].includes(payrun.status)
              }
              onClick={handleCancel}
            >
              {busy === "cancel" ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Ban />
              )}
              Cancel
            </Button>
          </CardContent>
        </Card>

        {validation && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">
                Validation —{" "}
                {validation.valid
                  ? "No issues"
                  : `${validation.warning_count} warning(s)`}
              </CardTitle>
            </CardHeader>
            {!validation.valid && (
              <CardContent className="space-y-2">
                {validation.warnings.map((w, i) => (
                  <div
                    key={i}
                    className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800"
                  >
                    <span className="font-medium">{w.employee_number}</span> —{" "}
                    {w.message}
                  </div>
                ))}
              </CardContent>
            )}
          </Card>
        )}

        {sendResult && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Payslip delivery result</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">
                Sent {sendResult.sent} of {sendResult.total}
                {sendResult.failed > 0 && (
                  <span className="text-destructive">
                    {" "}
                    — {sendResult.failed} failed
                  </span>
                )}
              </p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Payslips</CardTitle>
          </CardHeader>
          <CardContent>
            {payslipsLoading ? (
              <LoadingBanner label="Loading payslips…" />
            ) : !payslips || payslips.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No payslips yet — compute payroll to generate them.
              </p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead>Gross</TableHead>
                    <TableHead>Deductions</TableHead>
                    <TableHead>Tax</TableHead>
                    <TableHead>Net</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {payslips.map((slip) => (
                    <TableRow
                      key={slip.id}
                      className="cursor-pointer"
                      onClick={() =>
                        router.push(
                          `/dashboard/payroll/payslips?payslip_id=${slip.id}`,
                        )
                      }
                    >
                      <TableCell>
                        {slip.employee_name}{" "}
                        <span className="text-xs text-muted-foreground">
                          {slip.employee_number}
                        </span>
                      </TableCell>
                      <TableCell>{money(Number(slip.gross_amount))}</TableCell>
                      <TableCell>
                        {money(Number(slip.deductions_amount))}
                      </TableCell>
                      <TableCell>{money(Number(slip.tax_amount))}</TableCell>
                      <TableCell>{money(Number(slip.net_amount))}</TableCell>
                      <TableCell>
                        <StatusBadge status={slip.status} />
                      </TableCell>
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
