"use client";

import { useState } from "react";
import { Wallet2, Plus } from "lucide-react";

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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { EmptyState } from "@/components/shared/empty-state";
import {
  useAllocations,
  useTimeOffTypes,
  timeOffApi,
} from "@/hooks/useTimeOff";
import { useEmployees } from "@/hooks/useEmployees";
import { ApiError } from "@/lib/api";

function NewAllocationDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const { data: employees } = useEmployees();
  const { data: types } = useTimeOffTypes(true);
  const [employeeId, setEmployeeId] = useState("");
  const [typeId, setTypeId] = useState("");
  const [year, setYear] = useState(String(new Date().getFullYear()));
  const [allocatedDays, setAllocatedDays] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await timeOffApi.createAllocation({
        employee_id: employeeId,
        time_off_type_id: typeId,
        year: Number(year),
        allocated_days: Number(allocatedDays),
      });
      setOpen(false);
      setEmployeeId("");
      setTypeId("");
      setAllocatedDays("");
      onCreated();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not create allocation.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        <Plus /> New allocation
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New time-off allocation</DialogTitle>
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
              <Label htmlFor="year">Year</Label>
              <Input
                id="year"
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="days">Allocated days</Label>
              <Input
                id="days"
                type="number"
                min={0}
                value={allocatedDays}
                onChange={(e) => setAllocatedDays(e.target.value)}
                required
              />
            </div>
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
              {saving ? "Saving…" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function AllocationsPage() {
  const { data: employees } = useEmployees();
  const { data: types } = useTimeOffTypes();
  const { data: allocations, loading, error, reload } = useAllocations();

  const employeeName = (id: string) => {
    const emp = employees?.find((e) => e.id === id);
    return emp ? `${emp.first_name} ${emp.last_name}` : id;
  };
  const typeName = (id: string) => types?.find((t) => t.id === id)?.name ?? id;

  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title="Time-Off Allocations"
        description="Allocated vs. used balances — approved requests consume this automatically."
        actions={<NewAllocationDialog onCreated={reload} />}
      />
      <div className="pp-page-content flex-1 space-y-4 p-4 sm:p-6">
        {error && <ErrorBanner message={error} />}
        {loading ? (
          <LoadingBanner label="Loading allocations…" />
        ) : !allocations || allocations.length === 0 ? (
          <EmptyState
            icon={Wallet2}
            title="No allocations yet"
            description="Allocate leave days to an employee for a given year."
          />
        ) : (
          <div className="overflow-hidden rounded-xl border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Year</TableHead>
                  <TableHead>Allocated</TableHead>
                  <TableHead>Used</TableHead>
                  <TableHead>Remaining</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {allocations.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell className="font-medium">
                      {employeeName(a.employee_id)}
                    </TableCell>
                    <TableCell>{typeName(a.time_off_type_id)}</TableCell>
                    <TableCell>{a.year}</TableCell>
                    <TableCell>{a.allocated_days}</TableCell>
                    <TableCell>{a.used_days}</TableCell>
                    <TableCell>
                      {(Number(a.allocated_days) - Number(a.used_days)).toFixed(
                        2,
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
