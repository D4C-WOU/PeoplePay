"use client";

import { useState } from "react";
import { ShieldCheck } from "lucide-react";

import { Header } from "@/components/layout/header";
import { DataTable } from "@/components/shared/data-table";
import { FilterBar } from "@/components/shared/filter-bar";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useUsers, userApi } from "@/hooks/useUsers";
import { useAuth } from "@/hooks/useAuth";
import { ApiError } from "@/lib/api";
import { ROLE_LABELS, type UserRole } from "@/lib/auth";
import type { User } from "@/types/auth";

const roles: UserRole[] = [
  "ADMIN",
  "HR_MANAGER",
  "MANAGER",
  "EMPLOYEE",
  "PAYROLL_MANAGER",
  "PAYROLL_USER",
];

function UserActions({
  user,
  currentUserId,
  onSaved,
}: {
  user: User;
  currentUserId?: string;
  onSaved: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function update(data: { role?: UserRole; is_active?: boolean }) {
    setBusy(true);
    setError(null);
    try {
      await userApi.update(user.id, data);
      onSaved();
    } catch (requestError) {
      setError(
        requestError instanceof ApiError
          ? requestError.message
          : "Unable to update user.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-w-52 items-center gap-2">
      <Select
        value={user.role}
        onValueChange={(value) => update({ role: value as UserRole })}
        disabled={busy}
      >
        <SelectTrigger className="h-8 w-40">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {roles.map((role) => (
            <SelectItem key={role} value={role}>
              {ROLE_LABELS[role]}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button
        variant="outline"
        size="sm"
        disabled={busy || user.id === currentUserId}
        onClick={() => update({ is_active: !user.is_active })}
      >
        {user.is_active ? "Deactivate" : "Activate"}
      </Button>
      {error && <span className="text-xs text-destructive">{error}</span>}
    </div>
  );
}

export default function UsersPage() {
  const { data: users, loading, error, reload } = useUsers();
  const { user: currentUser } = useAuth();
  const [query, setQuery] = useState("");
  const rows = (users ?? []).filter((user) =>
    user.email.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Users"
        description="Manage access, roles, and account status for PeoplePay users."
      />
      <div className="flex-1 space-y-4 p-4 sm:p-6">
        <FilterBar
          search={query}
          onSearchChange={setQuery}
          searchPlaceholder="Search by email"
          hasActiveFilters={Boolean(query)}
          onClear={() => setQuery("")}
        />
        <DataTable
          rows={rows}
          rowKey={(user) => user.id}
          loading={loading}
          error={error}
          emptyIcon={ShieldCheck}
          emptyTitle="No users found"
          emptyDescription="Users created through the backend will appear here."
          columns={[
            {
              key: "email",
              header: "User",
              render: (user) => (
                <span className="font-medium">{user.email}</span>
              ),
            },
            {
              key: "role",
              header: "Role",
              render: (user) => ROLE_LABELS[user.role],
            },
            {
              key: "status",
              header: "Status",
              render: (user) => (
                <StatusBadge status={user.is_active ? "ACTIVE" : "INACTIVE"} />
              ),
            },
            {
              key: "actions",
              header: "Actions",
              render: (user) => (
                <UserActions
                  user={user}
                  currentUserId={currentUser?.id}
                  onSaved={reload}
                />
              ),
            },
          ]}
        />
      </div>
    </div>
  );
}
