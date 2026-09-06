"use client";

import { useState } from "react";
import { Building2, Loader2, Plus } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { DataTable } from "@/components/shared/data-table";
import { FilterBar } from "@/components/shared/filter-bar";

import { useDepartments, departmentApi } from "@/hooks/useEmployees";

import { ApiError } from "@/lib/api";

function DepartmentDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);

  const [name, setName] = useState("");
  const [code, setCode] = useState("");

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function resetForm() {
    setName("");
    setCode("");
    setError(null);
  }

  function handleOpenChange(value: boolean) {
    if (saving) return;

    setOpen(value);

    if (!value) {
      resetForm();
    }
  }

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (saving) return;

    setError(null);

    const cleanName = name.trim();
    const cleanCode = code.trim().toUpperCase();

    if (!cleanName) {
      setError("Department name is required.");
      return;
    }

    if (!cleanCode) {
      setError("Department code is required.");
      return;
    }

    if (!/^[A-Z0-9_-]+$/.test(cleanCode)) {
      setError(
        "Department code can only contain letters, numbers, hyphens and underscores.",
      );
      return;
    }

    setSaving(true);

    try {
      await departmentApi.create({
        name: cleanName,
        code: cleanCode,
        is_active: true,
      });

      setOpen(false);
      resetForm();
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
        New department
      </Button>

      <DialogContent className="w-[calc(100%-2rem)] sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>New department</DialogTitle>
        </DialogHeader>

        <form onSubmit={submit} className="flex flex-col gap-5">
          <div className="flex flex-col gap-2">
            <Label htmlFor="department-name">Department name</Label>

            <Input
              id="department-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Engineering"
              disabled={saving}
              autoFocus
              required
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="department-code">Department code</Label>

            <Input
              id="department-code"
              value={code}
              onChange={(event) => setCode(event.target.value.toUpperCase())}
              placeholder="ENG"
              maxLength={20}
              disabled={saving}
              required
            />

            <p className="text-xs text-muted-foreground">
              Use a short unique code such as ENG, HR or FIN.
            </p>
          </div>

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

            <Button
              type="submit"
              disabled={saving || !name.trim() || !code.trim()}
            >
              {saving ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="size-4" />
                  Create department
                </>
              )}
            </Button>
          </DialogFooter>
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
