"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
import { useDepartments, employeeApi } from "@/hooks/useEmployees";
import { ApiError } from "@/lib/api";
import type { Employee, EmployeeType } from "@/types/employee";

export function EmployeeForm({ employee }: { employee?: Employee }) {
  const router = useRouter();
  const { data: departments } = useDepartments();
  const isEdit = !!employee;

  const [employeeNumber, setEmployeeNumber] = useState(
    employee?.employee_number ?? "",
  );
  const [firstName, setFirstName] = useState(employee?.first_name ?? "");
  const [lastName, setLastName] = useState(employee?.last_name ?? "");
  const [email, setEmail] = useState(employee?.email ?? "");
  const [phone, setPhone] = useState(employee?.phone ?? "");
  const [hireDate, setHireDate] = useState(employee?.hire_date ?? "");
  const [jobTitle, setJobTitle] = useState(employee?.job_title ?? "");
  const [employeeType, setEmployeeType] = useState<EmployeeType>(
    employee?.employee_type ?? "FULL_TIME",
  );
  const [departmentId, setDepartmentId] = useState(
    employee?.department_id ?? "",
  );
  const [bankName, setBankName] = useState(employee?.bank_name ?? "");
  const [bankAccountNumber, setBankAccountNumber] = useState(
    employee?.bank_account_number ?? "",
  );
  const [bankIfsc, setBankIfsc] = useState(employee?.bank_ifsc ?? "");
  const [address, setAddress] = useState(employee?.address ?? "");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);

    const payload = {
      employee_number: employeeNumber,
      first_name: firstName,
      last_name: lastName,
      email,
      phone: phone || undefined,
      hire_date: hireDate,
      job_title: jobTitle || undefined,
      employee_type: employeeType,
      department_id: departmentId || undefined,
      bank_name: bankName || undefined,
      bank_account_number: bankAccountNumber || undefined,
      bank_ifsc: bankIfsc || undefined,
      address: address || undefined,
      status: employee?.status ?? "ACTIVE",
    };

    try {
      if (isEdit && employee) {
        await employeeApi.update(employee.id, payload);
      } else {
        await employeeApi.create(payload);
      }
      router.push("/dashboard/employees");
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not save employee.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card className="rounded-2xl border border-(--pp-border) bg-(--pp-card-bg) shadow-(--pp-shadow)">
      <CardContent className="p-5 sm:p-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label htmlFor="employee-number">Employee number</Label>
              <Input
                id="employee-number"
                value={employeeNumber}
                onChange={(e) => setEmployeeNumber(e.target.value)}
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="hire-date">Hire date</Label>
              <Input
                id="hire-date"
                type="date"
                value={hireDate}
                onChange={(e) => setHireDate(e.target.value)}
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="first-name">First name</Label>
              <Input
                id="first-name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="last-name">Last name</Label>
              <Input
                id="last-name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                value={phone ?? ""}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="job-title">Job title</Label>
              <Input
                id="job-title"
                value={jobTitle ?? ""}
                onChange={(e) => setJobTitle(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label>Employee type</Label>
              <Select
                value={employeeType}
                onValueChange={(v) => setEmployeeType(v as EmployeeType)}
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
              <Label>Department</Label>
              <Select
                value={departmentId ?? ""}
                onValueChange={setDepartmentId}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {departments?.map((dept) => (
                    <SelectItem key={dept.id} value={dept.id}>
                      {dept.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label htmlFor="bank-name">Bank name</Label>
              <Input
                id="bank-name"
                value={bankName ?? ""}
                onChange={(e) => setBankName(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="bank-account">Account number</Label>
              <Input
                id="bank-account"
                value={bankAccountNumber ?? ""}
                onChange={(e) => setBankAccountNumber(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="bank-ifsc">IFSC</Label>
              <Input
                id="bank-ifsc"
                value={bankIfsc ?? ""}
                onChange={(e) => setBankIfsc(e.target.value)}
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="address">Address</Label>
            <Textarea
              id="address"
              value={address ?? ""}
              onChange={(e) => setAddress(e.target.value)}
            />
          </div>

          {error && (
            <p className="rounded-lg border border-destructive/20 bg-destructive/10 px-3 py-2.5 text-sm text-destructive">
              {error}
            </p>
          )}

          <div className="-mx-5 -mb-5 mt-1 flex flex-col-reverse gap-2 rounded-b-2xl border-t border-(--pp-border) bg-(--pp-page-bg) p-4 sm:-mx-6 sm:-mb-6 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/dashboard/employees")}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving…" : isEdit ? "Save changes" : "Create employee"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
