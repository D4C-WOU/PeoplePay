"use client";

import { useState } from "react";
import Link from "next/link";
import { Plus, Users } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { StatusBadge } from "@/components/shared/status-badge";
import { DataTable } from "@/components/shared/data-table";
import { FilterBar } from "@/components/shared/filter-bar";
import { useDepartments, usePaginatedEmployees } from "@/hooks/useEmployees";

const PAGE_SIZE = 10;

export default function EmployeesPage() {
  const [departmentId, setDepartmentId] = useState<string>("all");
  const [status, setStatus] = useState<string>(() =>
    typeof window !== "undefined"
      ? (new URLSearchParams(window.location.search).get("status") ?? "all")
      : "all",
  );
  const [query, setQuery] = useState<string>(() =>
    typeof window !== "undefined"
      ? (new URLSearchParams(window.location.search).get("search") ?? "")
      : "",
  );
  const [page, setPage] = useState(1);

  const { data: departments } = useDepartments();
  const {
    data: employeePage,
    loading,
    error,
  } = usePaginatedEmployees({
    department_id: departmentId === "all" ? undefined : departmentId,
    status: status === "all" ? undefined : status,
    q: query.trim() || undefined,
    page,
    page_size: PAGE_SIZE,
  });
  const employees = employeePage?.items ?? [];

  const departmentName = (id?: string | null) =>
    departments?.find((d) => d.id === id)?.name ?? "Unassigned";

  function updateDepartment(value: string) {
    setDepartmentId(value);
    setPage(1);
  }

  function updateStatus(value: string) {
    setStatus(value);
    setPage(1);
  }

  function updateQuery(value: string) {
    setQuery(value);
    setPage(1);
  }

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Employees"
        description="The central record for every hire — contracts, attendance and leave connect back here."
        actions={
          <Button render={<Link href="/dashboard/employees/new" />}>
            <Plus /> New employee
          </Button>
        }
      />

      <div className="flex-1 space-y-4 p-4 sm:p-6">
        <FilterBar
          search={query}
          onSearchChange={updateQuery}
          searchPlaceholder="Search by name, number or email"
          hasActiveFilters={Boolean(
            query || departmentId !== "all" || status !== "all",
          )}
          onClear={() => {
            setQuery("");
            setDepartmentId("all");
            setStatus("all");
            setPage(1);
          }}
        >
          <Select value={departmentId} onValueChange={updateDepartment}>
            <SelectTrigger className="w-44">
              <SelectValue placeholder="Department" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All departments</SelectItem>
              {departments?.map((dept) => (
                <SelectItem key={dept.id} value={dept.id}>
                  {dept.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={status} onValueChange={updateStatus}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              <SelectItem value="ACTIVE">Active</SelectItem>
              <SelectItem value="ON_LEAVE">On leave</SelectItem>
              <SelectItem value="TERMINATED">Terminated</SelectItem>
            </SelectContent>
          </Select>
        </FilterBar>

        <DataTable
          rows={employees}
          rowKey={(employee) => employee.id}
          loading={loading}
          error={error}
          emptyIcon={Users}
          emptyTitle="No employees match these filters"
          emptyDescription="Try clearing a filter, or add a new employee to get started."
          page={employeePage?.page}
          pageSize={employeePage?.page_size}
          total={employeePage?.total}
          pages={employeePage?.pages}
          onPageChange={setPage}
          columns={[
            {
              key: "employee",
              header: "Employee",
              render: (emp) => (
                <Link
                  href={`/dashboard/employees/${emp.id}`}
                  className="flex items-center gap-2.5"
                >
                  <Avatar size="sm">
                    <AvatarFallback>
                      {emp.first_name[0]}
                      {emp.last_name[0]}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium">
                      {emp.first_name} {emp.last_name}
                    </p>
                    <p className="text-xs text-muted-foreground">{emp.email}</p>
                  </div>
                </Link>
              ),
            },
            {
              key: "number",
              header: "Number",
              className: "text-muted-foreground",
              render: (emp) => emp.employee_number,
            },
            {
              key: "department",
              header: "Department",
              render: (emp) => departmentName(emp.department_id),
            },
            {
              key: "job",
              header: "Job title",
              render: (emp) => emp.job_title ?? "—",
            },
            {
              key: "type",
              header: "Type",
              className: "capitalize text-muted-foreground",
              render: (emp) =>
                emp.employee_type.replaceAll("_", " ").toLowerCase(),
            },
            {
              key: "status",
              header: "Status",
              render: (emp) => <StatusBadge status={emp.status} />,
            },
          ]}
        />
      </div>
    </div>
  );
}
