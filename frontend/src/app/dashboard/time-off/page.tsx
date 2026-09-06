"use client";

import { useState } from "react";
import Link from "next/link";
import { CalendarRange, Plus, ArrowRight } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/shared/data-table";
import { useTimeOffTypes, timeOffApi } from "@/hooks/useTimeOff";
import { ApiError } from "@/lib/api";

function NewTypeDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [defaultAllocation, setDefaultAllocation] = useState("0");
  const [isPaid, setIsPaid] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await timeOffApi.createType({
        code,
        name,
        description: description || undefined,
        default_allocation: Number(defaultAllocation),
        is_paid: isPaid,
        is_active: true,
      });
      setOpen(false);
      setCode("");
      setName("");
      setDescription("");
      onCreated();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not create time-off type.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        <Plus /> New type
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New time-off type</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="code">Code</Label>
              <Input
                id="code"
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                required
                placeholder="ANNUAL"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="allocation">Default allocation (days)</Label>
              <Input
                id="allocation"
                type="number"
                min={0}
                value={defaultAllocation}
                onChange={(e) => setDefaultAllocation(e.target.value)}
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="Annual Leave"
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
          <label className="flex items-center gap-2 text-sm">
            <Checkbox
              checked={isPaid}
              onCheckedChange={(v) => setIsPaid(!!v)}
            />
            Paid leave
          </label>
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

export default function TimeOffPage() {
  const { data: types, loading, error, reload } = useTimeOffTypes();

  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title="Time Off"
        description="Configure leave types; allocations and requests live in their own tabs."
        actions={<NewTypeDialog onCreated={reload} />}
      />
      <div className="pp-page-content flex-1 space-y-4 p-4 sm:p-6">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Card>
            <CardContent className="flex items-center justify-between pt-1">
              <p className="text-sm font-medium">Allocations</p>
              <Button
                variant="outline"
                size="sm"
                nativeButton={false}
                render={<Link href="/dashboard/time-off/allocations" />}
              >
                Manage <ArrowRight />
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center justify-between pt-1">
              <p className="text-sm font-medium">Requests</p>
              <Button
                variant="outline"
                size="sm"
                nativeButton={false}
                render={<Link href="/dashboard/time-off/requests" />}
              >
                Manage <ArrowRight />
              </Button>
            </CardContent>
          </Card>
        </div>

        <DataTable
          rows={types ?? []}
          rowKey={(type) => type.id}
          loading={loading}
          error={error}
          emptyIcon={CalendarRange}
          emptyTitle="No time-off types yet"
          emptyDescription="Create a type such as Annual Leave or Sick Leave to get started."
          columns={[
            {
              key: "code",
              header: "Code",
              className: "font-mono text-xs",
              render: (type) => type.code,
            },
            {
              key: "name",
              header: "Name",
              render: (type) => (
                <span className="font-medium">{type.name}</span>
              ),
            },
            {
              key: "allocation",
              header: "Default allocation",
              render: (type) => `${type.default_allocation} days`,
            },
            {
              key: "paid",
              header: "Paid",
              render: (type) => (
                <Badge variant={type.is_paid ? "default" : "secondary"}>
                  {type.is_paid ? "Paid" : "Unpaid"}
                </Badge>
              ),
            },
            {
              key: "status",
              header: "Status",
              render: (type) => (
                <Badge variant={type.is_active ? "default" : "secondary"}>
                  {type.is_active ? "Active" : "Inactive"}
                </Badge>
              ),
            },
          ]}
        />
      </div>
    </div>
  );
}
