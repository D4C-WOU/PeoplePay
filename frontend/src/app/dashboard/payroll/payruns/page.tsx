"use client";

import { useState } from "react";
import Link from "next/link";
import { PlayCircle, Plus } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { StatusBadge } from "@/components/shared/status-badge";
import { DataTable } from "@/components/shared/data-table";
import { FilterBar } from "@/components/shared/filter-bar";
import {
  usePaginatedPayruns,
  useSalaryStructures,
  payrunApi,
} from "@/hooks/usePayroll";
import { useEmployees } from "@/hooks/useEmployees";
import { ApiError } from "@/lib/api";

const PAGE_SIZE = 10;

function money(value: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

function NewPayrunWizard({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState<1 | 2>(1);

  const { data: structures } = useSalaryStructures(true);
  const { data: employees } = useEmployees({ status: "ACTIVE" });

  const [structureId, setStructureId] = useState("");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [paymentDate, setPaymentDate] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const eligible = employees ?? [];

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleAll() {
    if (selected.size === eligible.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(eligible.map((e) => e.id)));
    }
  }

  function reset() {
    setStep(1);
    setStructureId("");
    setPeriodStart("");
    setPeriodEnd("");
    setPaymentDate("");
    setSelected(new Set());
    setError(null);
  }

  async function handleCreate() {
    setSaving(true);
    setError(null);
    try {
      await payrunApi.create({
        period_start: periodStart,
        period_end: periodEnd,
        payment_date: paymentDate || undefined,
        salary_structure_id: structureId,
        employee_ids: Array.from(selected),
      });
      setOpen(false);
      reset();
      onCreated();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not create pay run.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        setOpen(v);
        if (!v) reset();
      }}
    >
      <DialogTrigger render={<Button />}>
        <Plus /> New pay run
      </DialogTrigger>
      <DialogContent className="w-[min(92vw,760px)] max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {step === 1
              ? "New pay run — period & structure"
              : "Select employees"}
          </DialogTitle>
        </DialogHeader>

        {step === 1 && (
          <div className="space-y-3">
            <div className="space-y-1.5">
              <Label>Salary structure</Label>
              <Select value={structureId} onValueChange={setStructureId}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select structure" />
                </SelectTrigger>
                <SelectContent>
                  {structures?.map((s) => (
                    <SelectItem key={s.id} value={s.id}>
                      {s.name} ({s.code})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="ps">Period start</Label>
                <Input
                  id="ps"
                  type="date"
                  value={periodStart}
                  onChange={(e) => setPeriodStart(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="pe">Period end</Label>
                <Input
                  id="pe"
                  type="date"
                  value={periodEnd}
                  onChange={(e) => setPeriodEnd(e.target.value)}
                  required
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="pd">Payment date (optional)</Label>
              <Input
                id="pd"
                type="date"
                value={paymentDate}
                onChange={(e) => setPaymentDate(e.target.value)}
              />
            </div>
            <DialogFooter>
              <DialogClose render={<Button variant="outline" type="button" />}>
                Cancel
              </DialogClose>
              <Button
                type="button"
                disabled={!structureId || !periodStart || !periodEnd}
                onClick={() => setStep(2)}
              >
                Next: select employees
              </Button>
            </DialogFooter>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                {selected.size} of {eligible.length} selected
              </p>
              <Button
                variant="ghost"
                size="sm"
                type="button"
                onClick={toggleAll}
              >
                {selected.size === eligible.length ? "Clear all" : "Select all"}
              </Button>
            </div>
            <div className="max-h-72 overflow-y-auto rounded-lg border">
              {eligible.length === 0 ? (
                <p className="p-4 text-sm text-muted-foreground">
                  No active employees found.
                </p>
              ) : (
                eligible.map((emp) => (
                  <label
                    key={emp.id}
                    className="flex cursor-pointer items-center gap-2.5 border-b p-2.5 text-sm last:border-b-0 hover:bg-muted/50"
                  >
                    <Checkbox
                      checked={selected.has(emp.id)}
                      onCheckedChange={() => toggle(emp.id)}
                    />
                    <span>
                      {emp.first_name} {emp.last_name}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {emp.employee_number}
                    </span>
                  </label>
                ))
              )}
            </div>
            {error && (
              <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </p>
            )}
            <DialogFooter>
              <Button
                variant="outline"
                type="button"
                onClick={() => setStep(1)}
              >
                Back
              </Button>
              <Button
                type="button"
                disabled={saving || selected.size === 0}
                onClick={handleCreate}
              >
                {saving ? "Creating…" : `Create pay run (${selected.size})`}
              </Button>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default function PayrunsPage() {
  const [status, setStatus] = useState<string>("all");
  const [page, setPage] = useState(1);
  const {
    data: payrunPage,
    loading,
    error,
    reload,
  } = usePaginatedPayruns({
    status: status === "all" ? undefined : status,
    page,
    page_size: PAGE_SIZE,
  });
  const payruns = payrunPage?.items ?? [];

  function updateStatus(value: string) {
    setStatus(value);
    setPage(1);
  }

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Pay Runs"
        description="Select employees explicitly — the payrun contains only who you choose."
        actions={
          <NewPayrunWizard
            onCreated={() => {
              setPage(1);
              reload();
            }}
          />
        }
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
                <SelectItem value="PROCESSING">Processing</SelectItem>
                <SelectItem value="COMPLETED">Completed</SelectItem>
                <SelectItem value="CANCELLED">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </FilterBar>
        </div>
        <DataTable
          rows={payruns}
          rowKey={(run) => run.id}
          loading={loading}
          error={error}
          emptyIcon={PlayCircle}
          emptyTitle="No pay runs yet"
          emptyDescription="Start a new pay run to compute payslips for a period."
          page={payrunPage?.page}
          pageSize={payrunPage?.page_size}
          total={payrunPage?.total}
          pages={payrunPage?.pages}
          onPageChange={setPage}
          columns={[
            {
              key: "period",
              header: "Period",
              render: (run) => (
                <Link
                  href={`/dashboard/payroll/payruns/${run.id}`}
                  className="font-medium"
                >
                  {run.period_start} → {run.period_end}
                </Link>
              ),
            },
            {
              key: "payment",
              header: "Payment date",
              className: "text-muted-foreground",
              render: (run) => run.payment_date ?? "—",
            },
            {
              key: "employees",
              header: "Employees",
              render: (run) => run.employee_count,
            },
            {
              key: "net",
              header: "Net",
              render: (run) => money(Number(run.total_net)),
            },
            {
              key: "status",
              header: "Status",
              render: (run) => <StatusBadge status={run.status} />,
            },
          ]}
        />
      </div>
    </div>
  );
}
