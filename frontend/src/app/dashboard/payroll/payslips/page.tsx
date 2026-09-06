"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Download, Receipt } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StatusBadge } from "@/components/shared/status-badge";
import { DataTable } from "@/components/shared/data-table";
import { FilterBar } from "@/components/shared/filter-bar";
import { LoadingBanner } from "@/components/shared/state-banner";
import { usePaginatedPayslips, payslipApi } from "@/hooks/usePayroll";
import { ApiError } from "@/lib/api";
import type { Payslip } from "@/types/payroll";

const PAGE_SIZE = 10;

function money(value: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

function PayslipViewer({
  payslip,
  onClose,
}: {
  payslip: Payslip;
  onClose: () => void;
}) {
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  async function handleDownload() {
    setDownloading(true);
    setDownloadError(null);
    try {
      await payslipApi.downloadPdf(
        payslip.id,
        `payslip-${payslip.employee_number}.pdf`,
      );
    } catch (err) {
      setDownloadError(
        err instanceof ApiError ? err.message : "Could not download PDF.",
      );
    } finally {
      setDownloading(false);
    }
  }

  return (
    <Dialog open onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="w-[min(92vw,760px)] max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            Payslip — {payslip.employee_name} ({payslip.employee_number})
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rule</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Amount</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {payslip.lines
                .slice()
                .sort((a, b) => a.sequence - b.sequence)
                .map((line) => (
                  <TableRow key={line.id}>
                    <TableCell>{line.rule_name}</TableCell>
                    <TableCell className="capitalize text-muted-foreground">
                      {line.category.replaceAll("_", " ").toLowerCase()}
                    </TableCell>
                    <TableCell>
                      {money(Number(line.amount), payslip.currency)}
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>

          <div className="space-y-1 rounded-lg border p-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Gross</span>
              <span>
                {money(Number(payslip.gross_amount), payslip.currency)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Deductions</span>
              <span>
                {money(Number(payslip.deductions_amount), payslip.currency)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Tax</span>
              <span>{money(Number(payslip.tax_amount), payslip.currency)}</span>
            </div>
            <div className="flex justify-between border-t pt-1 font-semibold">
              <span>Net pay</span>
              <span>{money(Number(payslip.net_amount), payslip.currency)}</span>
            </div>
          </div>

          {downloadError && (
            <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {downloadError}
            </p>
          )}

          <Button
            className="w-full"
            disabled={payslip.status === "DRAFT" || downloading}
            onClick={handleDownload}
          >
            <Download /> {downloading ? "Downloading…" : "Download PDF"}
          </Button>
          {payslip.status === "DRAFT" && (
            <p className="text-center text-xs text-muted-foreground">
              PDF is available once the payrun is finalized.
            </p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

function PayslipsContent() {
  const searchParams = useSearchParams();
  const preselected = searchParams.get("payslip_id");
  const [status, setStatus] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [activePayslip, setActivePayslip] = useState<Payslip | null>(null);

  const {
    data: payslipPage,
    loading,
    error,
  } = usePaginatedPayslips({
    status: status === "all" ? undefined : status,
    page,
    page_size: PAGE_SIZE,
  });
  const payslips = payslipPage?.items ?? [];

  const shown = activePayslip ?? payslips.find((p) => p.id === preselected);

  function updateStatus(value: string) {
    setStatus(value);
    setPage(1);
  }

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Payslips"
        description="Every generated payslip, with a full component breakdown."
      />
      <div className="flex-1 space-y-4 p-4 sm:p-6">
        <div className="flex justify-center">
          <FilterBar
            className="w-full max-w-2xl justify-center"
            hasActiveFilters={status !== "all"}
            onClear={() => updateStatus("all")}
          >
            <Select value={status} onValueChange={updateStatus}>
              <SelectTrigger className="w-44 bg-white">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All statuses</SelectItem>
                <SelectItem value="DRAFT">Draft</SelectItem>
                <SelectItem value="FINALIZED">Finalized</SelectItem>
                <SelectItem value="PAID">Paid</SelectItem>
                <SelectItem value="CANCELLED">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </FilterBar>
        </div>

        <DataTable
          rows={payslips}
          rowKey={(slip) => slip.id}
          loading={loading}
          error={error}
          emptyIcon={Receipt}
          emptyTitle="No payslips yet"
          emptyDescription="Payslips appear here once a pay run has been computed."
          page={payslipPage?.page}
          pageSize={payslipPage?.page_size}
          total={payslipPage?.total}
          pages={payslipPage?.pages}
          onPageChange={setPage}
          onRowClick={setActivePayslip}
          columns={[
            {
              key: "employee",
              header: "Employee",
              render: (slip) => (
                <>
                  <span className="font-medium">{slip.employee_name}</span>{" "}
                  <span className="text-xs text-muted-foreground">
                    {slip.employee_number}
                  </span>
                </>
              ),
            },
            {
              key: "gross",
              header: "Gross",
              render: (slip) => money(Number(slip.gross_amount), slip.currency),
            },
            {
              key: "net",
              header: "Net",
              render: (slip) => money(Number(slip.net_amount), slip.currency),
            },
            {
              key: "status",
              header: "Status",
              render: (slip) => <StatusBadge status={slip.status} />,
            },
          ]}
        />
      </div>

      {shown && (
        <PayslipViewer payslip={shown} onClose={() => setActivePayslip(null)} />
      )}
    </div>
  );
}

export default function PayslipsPage() {
  return (
    <Suspense
      fallback={
        <div className="p-4 sm:p-6">
          <LoadingBanner label="Loading payslips…" />
        </div>
      }
    >
      <PayslipsContent />
    </Suspense>
  );
}
