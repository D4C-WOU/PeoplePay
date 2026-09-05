"use client";

import { useState } from "react";
import Link from "next/link";
import { Wallet, Plus } from "lucide-react";

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
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/shared/data-table";
import { useSalaryStructures, salaryStructureApi } from "@/hooks/usePayroll";
import { ApiError } from "@/lib/api";

function NewStructureDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [currency, setCurrency] = useState("INR");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await salaryStructureApi.create({
        code,
        name,
        description: description || undefined,
        currency,
        is_active: true,
      });
      setOpen(false);
      setCode("");
      setName("");
      setDescription("");
      onCreated();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not create structure.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        <Plus /> New structure
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New salary structure</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="space-y-1.5">
            <Label htmlFor="code">Code</Label>
            <Input
              id="code"
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              required
              placeholder="MONTHLY"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="Monthly Salary"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="currency">Currency</Label>
            <Input
              id="currency"
              value={currency}
              onChange={(e) => setCurrency(e.target.value.toUpperCase())}
              required
              maxLength={10}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
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
            <Button type="submit" disabled={saving}>
              {saving ? "Saving…" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function SalaryStructuresPage() {
  const { data: structures, loading, error, reload } = useSalaryStructures();

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Salary Structures"
        description="Structures group the salary rules that drive payslip generation."
        actions={<NewStructureDialog onCreated={reload} />}
      />
      <div className="flex-1 space-y-4 p-4 sm:p-6">
        <DataTable
          rows={structures ?? []}
          rowKey={(structure) => structure.id}
          loading={loading}
          error={error}
          emptyIcon={Wallet}
          emptyTitle="No salary structures yet"
          emptyDescription="Create a structure, then add salary rules to it."
          columns={[
            {
              key: "code",
              header: "Code",
              className: "font-mono text-xs",
              render: (structure) => structure.code,
            },
            {
              key: "name",
              header: "Name",
              render: (structure) => (
                <span className="font-medium">{structure.name}</span>
              ),
            },
            {
              key: "currency",
              header: "Currency",
              render: (structure) => structure.currency,
            },
            {
              key: "status",
              header: "Status",
              render: (structure) => (
                <Badge variant={structure.is_active ? "default" : "secondary"}>
                  {structure.is_active ? "Active" : "Inactive"}
                </Badge>
              ),
            },
            {
              key: "rules",
              header: "Rules",
              render: (structure) => (
                <Link
                  href={`/dashboard/salary/rules?structure_id=${structure.id}`}
                  className="text-sm underline-offset-2 hover:underline"
                  style={{ color: "var(--pp-brand)" }}
                >
                  View rules →
                </Link>
              ),
            },
          ]}
        />
      </div>
    </div>
  );
}
