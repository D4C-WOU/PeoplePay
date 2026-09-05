"use client";

import { useState } from "react";
import { Plus } from "lucide-react";

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
import { Textarea } from "@/components/ui/textarea";
import { useEmployees, useSchedules, contractApi } from "@/hooks/useEmployees";
import { useSalaryStructures } from "@/hooks/usePayroll";
import { ApiError } from "@/lib/api";
import type { ContractType } from "@/types/employee";

export function ContractDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const { data: employees } = useEmployees({ status: "ACTIVE" });
  const { data: structures } = useSalaryStructures(true);
  const { data: schedules } = useSchedules();

  const [employeeId, setEmployeeId] = useState("");
  const [salaryStructureId, setSalaryStructureId] = useState("");
  const [workScheduleId, setWorkScheduleId] = useState("");
  const [contractNumber, setContractNumber] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [contractType, setContractType] = useState<ContractType>("FULL_TIME");
  const [baseSalary, setBaseSalary] = useState("");
  const [currency, setCurrency] = useState("INR");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function reset() {
    setEmployeeId("");
    setSalaryStructureId("");
    setWorkScheduleId("");
    setContractNumber("");
    setStartDate("");
    setEndDate("");
    setContractType("FULL_TIME");
    setBaseSalary("");
    setCurrency("INR");
    setNotes("");
    setError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await contractApi.create({
        employee_id: employeeId,
        salary_structure_id: salaryStructureId,
        work_schedule_id: workScheduleId || undefined,
        contract_number: contractNumber,
        start_date: startDate,
        end_date: endDate || undefined,
        contract_type: contractType,
        base_salary: Number(baseSalary),
        currency,
        notes: notes || undefined,
      });
      setOpen(false);
      reset();
      onCreated();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not create contract.",
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
        <Plus /> New contract
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>New contract</DialogTitle>
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
                    {emp.first_name} {emp.last_name} ({emp.employee_number})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Salary structure</Label>
              <Select
                value={salaryStructureId}
                onValueChange={setSalaryStructureId}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select structure" />
                </SelectTrigger>
                <SelectContent>
                  {structures?.map((s) => (
                    <SelectItem key={s.id} value={s.id}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Work schedule (optional)</Label>
              <Select value={workScheduleId} onValueChange={setWorkScheduleId}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select schedule" />
                </SelectTrigger>
                <SelectContent>
                  {schedules?.map((s) => (
                    <SelectItem key={s.id} value={s.id}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="contract-number">Contract number</Label>
            <Input
              id="contract-number"
              value={contractNumber}
              onChange={(e) => setContractNumber(e.target.value)}
              placeholder="CTR-EMP006"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="start-date">Start date</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="end-date">End date (optional)</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Contract type</Label>
              <Select
                value={contractType}
                onValueChange={(v) => setContractType(v as ContractType)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="FULL_TIME">Full time</SelectItem>
                  <SelectItem value="PART_TIME">Part time</SelectItem>
                  <SelectItem value="CONTRACT">Contract</SelectItem>
                  <SelectItem value="INTERN">Intern</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="base-salary">Base salary</Label>
              <Input
                id="base-salary"
                type="number"
                min={0}
                step="0.01"
                value={baseSalary}
                onChange={(e) => setBaseSalary(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="currency">Currency</Label>
            <Input
              id="currency"
              value={currency}
              onChange={(e) => setCurrency(e.target.value.toUpperCase())}
              maxLength={10}
              required
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="notes">Notes (optional)</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
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
            <Button
              type="submit"
              disabled={
                saving || !employeeId || !salaryStructureId || !contractNumber
              }
            >
              {saving ? "Saving…" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
