"use client";

import { useState } from "react";
import { CalendarDays, Check, Plus, X, Ban } from "lucide-react";

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
import { Textarea } from "@/components/ui/textarea";
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
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { EmptyState } from "@/components/shared/empty-state";
import {
  useTimeOffRequests,
  useTimeOffTypes,
  timeOffApi,
} from "@/hooks/useTimeOff";
import { useEmployees } from "@/hooks/useEmployees";
import { ApiError } from "@/lib/api";

function NewRequestDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const { data: employees } = useEmployees();
  const { data: types } = useTimeOffTypes(true);
  const [employeeId, setEmployeeId] = useState("");
  const [typeId, setTypeId] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await timeOffApi.createRequest({
        employee_id: employeeId,
        time_off_type_id: typeId,
        start_date: startDate,
        end_date: endDate,
        reason: reason || undefined,
      });
      setOpen(false);
      setEmployeeId("");
      setTypeId("");
      setStartDate("");
      setEndDate("");
      setReason("");
      onCreated();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not create request.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        <Plus /> New request
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New time-off request</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="space-y-1.5">
            <Label>Employee</Label>
            <Select value={employeeId} onValueChange={setEmployeeId}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select employee" />
              </SelectTrigger>
              <SelectContent>
                {employees?.map((emp) => (
                  <SelectItem key={emp.id} value={emp.id}>
                    {emp.first_name} {emp.last_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label>Time-off type</Label>
            <Select value={typeId} onValueChange={setTypeId}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                {types?.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="start">Start date</Label>
              <Input
                id="start"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="end">End date</Label>
              <Input
                id="end"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="reason">Reason (optional)</Label>
            <Textarea
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </div>
          {error && (
            <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </p>
          )}
          <DialogFooter>
            <DialogClose render={<Button variant="outline" type="button" />}>
              Cancel
            </DialogClose>
            <Button type="submit" disabled={saving || !employeeId || !typeId}>
              {saving ? "Submitting…" : "Submit request"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function TimeOffRequestsPage() {
  const [status, setStatus] = useState<string>("all");
  const { data: employees } = useEmployees();
  const { data: types } = useTimeOffTypes();
  const {
    data: requests,
    loading,
    error,
    reload,
  } = useTimeOffRequests({ status: status === "all" ? undefined : status });

  const [rowBusy, setRowBusy] = useState<string | null>(null);
  const [rowError, setRowError] = useState<string | null>(null);

  const employeeName = (id: string) => {
    const emp = employees?.find((e) => e.id === id);
    return emp ? `${emp.first_name} ${emp.last_name}` : id;
  };
  const typeName = (id: string) => types?.find((t) => t.id === id)?.name ?? id;

  async function handleAction(
    id: string,
    action: "approve" | "reject" | "cancel",
  ) {
    setRowBusy(id + action);
    setRowError(null);
    try {
      if (action === "approve") await timeOffApi.approve(id);
      if (action === "reject") await timeOffApi.reject(id);
      if (action === "cancel") await timeOffApi.cancel(id);
      reload();
    } catch (err) {
      setRowError(
        err instanceof ApiError ? err.message : `Could not ${action}.`,
      );
    } finally {
      setRowBusy(null);
    }
  }

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Time-Off Requests"
        description="Pending → Approved / Refused. Approvals reduce the employee's allocation."
        actions={<NewRequestDialog onCreated={reload} />}
      />
      <div className="flex-1 space-y-4 p-4 sm:p-6">
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-44">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="PENDING">Pending</SelectItem>
            <SelectItem value="APPROVED">Approved</SelectItem>
            <SelectItem value="REJECTED">Rejected</SelectItem>
            <SelectItem value="CANCELLED">Cancelled</SelectItem>
          </SelectContent>
        </Select>

        {error && <ErrorBanner message={error} />}
        {rowError && <ErrorBanner message={rowError} />}
        {loading ? (
          <LoadingBanner label="Loading requests…" />
        ) : !requests || requests.length === 0 ? (
          <EmptyState
            icon={CalendarDays}
            title="No requests match this filter"
            description="Time-off requests will appear here once submitted."
          />
        ) : (
          <div className="overflow-hidden rounded-xl border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Dates</TableHead>
                  <TableHead>Days</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {requests.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-medium">
                      {employeeName(r.employee_id)}
                    </TableCell>
                    <TableCell>{typeName(r.time_off_type_id)}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {r.start_date} → {r.end_date}
                    </TableCell>
                    <TableCell>{r.requested_days}</TableCell>
                    <TableCell>
                      <StatusBadge status={r.status} />
                    </TableCell>
                    <TableCell>
                      {r.status === "PENDING" && (
                        <div className="flex gap-1.5">
                          <Button
                            size="icon-sm"
                            variant="outline"
                            disabled={!!rowBusy}
                            onClick={() => handleAction(r.id, "approve")}
                            title="Approve"
                          >
                            <Check />
                          </Button>
                          <Button
                            size="icon-sm"
                            variant="outline"
                            disabled={!!rowBusy}
                            onClick={() => handleAction(r.id, "reject")}
                            title="Reject"
                          >
                            <X />
                          </Button>
                        </div>
                      )}
                      {r.status === "APPROVED" && (
                        <Button
                          size="icon-sm"
                          variant="outline"
                          disabled={!!rowBusy}
                          onClick={() => handleAction(r.id, "cancel")}
                          title="Cancel"
                        >
                          <Ban />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}
