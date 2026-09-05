"use client";

import { useState } from "react";
import { Building2, Plus } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { DataTable } from "@/components/shared/data-table";
import { FilterBar } from "@/components/shared/filter-bar";
import { useDepartments, departmentApi } from "@/hooks/useEmployees";
import { ApiError } from "@/lib/api";

type DepartmentFormProps = { onCreated: () => void };

function DepartmentDialog({ onCreated }: DepartmentFormProps) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await departmentApi.create({
        name,
        code: code.toUpperCase(),
        is_active: true,
      });
      setOpen(false);
      setName("");
      setCode("");
      onCreated();
    } catch (requestError) {
      setError(
        requestError instanceof ApiError
          ? requestError.message
          : "Unable to create department.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <Button>
            <Plus /> New department
          </Button>
        }
      />
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New department</DialogTitle>
        </DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="department-name">Name</Label>
            <Input
              id="department-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="department-code">Code</Label>
            <Input
              id="department-code"
              value={code}
              onChange={(event) => setCode(event.target.value)}
              required
            />
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button type="submit" disabled={saving}>
            {saving ? "Creating..." : "Create department"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function DepartmentsPage() {
  const { data: departments, loading, error, reload } = useDepartments();
  const [query, setQuery] = useState("");
  const rows = (departments ?? []).filter((department) =>
    `${department.name} ${department.code}`
      .toLowerCase()
      .includes(query.toLowerCase()),
  );

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Departments"
        description="Organize employees into the teams that drive workforce and payroll reporting."
        actions={<DepartmentDialog onCreated={reload} />}
      />
      <div className="flex-1 space-y-4 p-4 sm:p-6">
        <FilterBar
          search={query}
          onSearchChange={setQuery}
          searchPlaceholder="Search departments"
          hasActiveFilters={Boolean(query)}
          onClear={() => setQuery("")}
        />
        <DataTable
          rows={rows}
          rowKey={(department) => department.id}
          loading={loading}
          error={error}
          emptyIcon={Building2}
          emptyTitle="No departments yet"
          emptyDescription="Create a department to organize your employee records."
          columns={[
            {
              key: "name",
              header: "Department",
              render: (department) => (
                <span className="font-medium">{department.name}</span>
              ),
            },
            {
              key: "code",
              header: "Code",
              className: "text-muted-foreground",
              render: (department) => department.code,
            },
            {
              key: "status",
              header: "Status",
              render: (department) =>
                department.is_active ? "Active" : "Inactive",
            },
          ]}
        />
      </div>
    </div>
  );
}
