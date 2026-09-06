"use client";

import { useState } from "react";
import { Loader2, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
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

  const { data: employees, loading: employeesLoading } = useEmployees({
    status: "ACTIVE",
  });

  const { data: structures, loading: structuresLoading } =
    useSalaryStructures(true);

  const { data: schedules, loading: schedulesLoading } = useSchedules();

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

  function resetForm() {
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

  function handleOpenChange(value: boolean) {
    if (saving) return;

    setOpen(value);

    if (!value) {
      resetForm();
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (saving) return;

    setError(null);

    const cleanContractNumber = contractNumber.trim();
    const cleanCurrency = currency.trim().toUpperCase();
    const cleanNotes = notes.trim();

    if (!employeeId) {
      setError("Please select an employee.");
      return;
    }

    if (!salaryStructureId) {
      setError("Please select a salary structure.");
      return;
    }

    if (!cleanContractNumber) {
      setError("Contract number is required.");
      return;
    }

    if (!startDate) {
      setError("Start date is required.");
      return;
    }

    if (endDate && endDate < startDate) {
      setError("End date cannot be before the start date.");
      return;
    }

    if (!baseSalary.trim()) {
      setError("Base salary is required.");
      return;
    }

    const salary = Number(baseSalary);

    if (!Number.isFinite(salary) || salary < 0) {
      setError("Base salary must be a valid positive number.");
      return;
    }

    if (!cleanCurrency) {
      setError("Currency is required.");
      return;
    }

    setSaving(true);

    try {
      await contractApi.create({
        employee_id: employeeId,
        salary_structure_id: salaryStructureId,
        work_schedule_id: workScheduleId || undefined,
        contract_number: cleanContractNumber,
        start_date: startDate,
        end_date: endDate || undefined,
        contract_type: contractType,
        base_salary: salary,
        currency: cleanCurrency,
        notes: cleanNotes || undefined,
      });

      setOpen(false);
      resetForm();
      onCreated();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not create contract.",
      );
    } finally {
      setSaving(false);
    }
  }

  const loadingDependencies =
    employeesLoading || structuresLoading || schedulesLoading;

  const cannotCreate =
    saving ||
    !employeeId ||
    !salaryStructureId ||
    !contractNumber.trim() ||
    !startDate ||
    !baseSalary.trim() ||
    !currency.trim();

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <Button
        type="button"
        onClick={() => {
          setError(null);
          setOpen(true);
        }}
        disabled={saving}
      >
        <Plus className="size-4" />
        New contract
      </Button>

      <DialogContent className="w-[calc(100%-2rem)] sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>New contract</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label>Employee</Label>

              <Select
                value={employeeId}
                onValueChange={setEmployeeId}
                disabled={saving || employeesLoading}
              >
                <SelectTrigger className="w-full">
                  <SelectValue
                    placeholder={
                      employeesLoading
                        ? "Loading employees..."
                        : "Select employee"
                    }
                  />
                </SelectTrigger>

                <SelectContent>
                  {employees?.length ? (
                    employees.map((employee) => (
                      <SelectItem key={employee.id} value={employee.id}>
                        {employee.first_name} {employee.last_name} (
                        {employee.employee_number})
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="__empty" disabled>
                      No active employees
                    </SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-2">
              <Label>Salary structure</Label>

              <Select
                value={salaryStructureId}
                onValueChange={setSalaryStructureId}
                disabled={saving || structuresLoading}
              >
                <SelectTrigger className="w-full">
                  <SelectValue
                    placeholder={
                      structuresLoading
                        ? "Loading structures..."
                        : "Select structure"
                    }
                  />
                </SelectTrigger>

                <SelectContent>
                  {structures?.length ? (
                    structures.map((structure) => (
                      <SelectItem key={structure.id} value={structure.id}>
                        {structure.name}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="__empty" disabled>
                      No active salary structures
                    </SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <Label>Work schedule</Label>

            <Select
              value={workScheduleId}
              onValueChange={setWorkScheduleId}
              disabled={saving || schedulesLoading}
            >
              <SelectTrigger className="w-full">
                <SelectValue
                  placeholder={
                    schedulesLoading
                      ? "Loading schedules..."
                      : "Select schedule (optional)"
                  }
                />
              </SelectTrigger>

              <SelectContent>
                {schedules?.length ? (
                  schedules.map((schedule) => (
                    <SelectItem key={schedule.id} value={schedule.id}>
                      {schedule.name}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItem value="__empty" disabled>
                    No schedules available
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="contract-number">Contract number</Label>

            <Input
              id="contract-number"
              value={contractNumber}
              onChange={(event) => setContractNumber(event.target.value)}
              placeholder="CTR-EMP006"
              disabled={saving}
              required
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label htmlFor="start-date">Start date</Label>

              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
                disabled={saving}
                required
              />
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="end-date">
                End date
                <span className="ml-1 text-muted-foreground">(optional)</span>
              </Label>

              <Input
                id="end-date"
                type="date"
                value={endDate}
                min={startDate || undefined}
                onChange={(event) => setEndDate(event.target.value)}
                disabled={saving}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label>Contract type</Label>

              <Select
                value={contractType}
                onValueChange={(value) =>
                  setContractType(value as ContractType)
                }
                disabled={saving}
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

            <div className="flex flex-col gap-2">
              <Label htmlFor="base-salary">Base salary</Label>

              <Input
                id="base-salary"
                type="number"
                min={0}
                step="0.01"
                value={baseSalary}
                onChange={(event) => setBaseSalary(event.target.value)}
                placeholder="50000"
                disabled={saving}
                required
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="currency">Currency</Label>

            <Input
              id="currency"
              value={currency}
              onChange={(event) =>
                setCurrency(event.target.value.toUpperCase())
              }
              maxLength={10}
              placeholder="INR"
              disabled={saving}
              required
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="notes">
              Notes
              <span className="ml-1 text-muted-foreground">(optional)</span>
            </Label>

            <Textarea
              id="notes"
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Additional contract notes..."
              disabled={saving}
              className="min-h-24 resize-none"
            />
          </div>

          {!loadingDependencies &&
            (!employees?.length || !structures?.length) && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                {!employees?.length &&
                  "There are no active employees available. "}
                {!structures?.length &&
                  "There are no active salary structures available."}
              </div>
            )}

          {error && (
            <div
              role="alert"
              className="rounded-lg border border-destructive/20 bg-destructive/10 px-3 py-2.5 text-sm text-destructive"
            >
              {error}
            </div>
          )}

          <DialogFooter>
            <DialogClose
              render={
                <Button type="button" variant="outline" disabled={saving} />
              }
            >
              Cancel
            </DialogClose>

            <Button type="submit" disabled={cannotCreate}>
              {saving ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="size-4" />
                  Create contract
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
