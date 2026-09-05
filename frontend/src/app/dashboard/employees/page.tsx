"use client";

import { useState } from "react";
import Link from "next/link";
import { Plus, Search, Users } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { StatusBadge } from "@/components/shared/status-badge";
import { EmptyState } from "@/components/shared/empty-state";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { Pagination } from "@/components/shared/pagination";
import { useDepartments, usePaginatedEmployees } from "@/hooks/useEmployees";

const PAGE_SIZE = 10;

export default function EmployeesPage() {
  const [departmentId, setDepartmentId] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [query, setQuery] = useState("");
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
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative min-w-[220px] flex-1">
            <Search className="absolute top-2 left-2.5 size-4 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => updateQuery(e.target.value)}
              placeholder="Search by name, number or email"
              className="pl-8"
            />
          </div>
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
        </div>

        {error && <ErrorBanner message={error} />}
        {loading ? (
          <LoadingBanner label="Loading employees…" />
        ) : employees.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No employees match these filters"
            description="Try clearing a filter, or add a new employee to get started."
          />
        ) : (
          <div className="overflow-hidden rounded-xl border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Number</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Job title</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {employees.map((emp) => (
                  <TableRow key={emp.id} className="cursor-pointer">
                    <TableCell>
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
                          <p className="text-xs text-muted-foreground">
                            {emp.email}
                          </p>
                        </div>
                      </Link>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {emp.employee_number}
                    </TableCell>
                    <TableCell>{departmentName(emp.department_id)}</TableCell>
                    <TableCell>{emp.job_title ?? "—"}</TableCell>
                    <TableCell className="capitalize text-muted-foreground">
                      {emp.employee_type.replaceAll("_", " ").toLowerCase()}
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={emp.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {employeePage && (
              <Pagination
                page={employeePage.page}
                pageSize={employeePage.page_size}
                total={employeePage.total}
                pages={employeePage.pages}
                onPageChange={setPage}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
