"use client";

import { useState } from "react";
import {
  Users,
  TrendingUp,
  Wallet,
  CalendarCheck,
  AlertCircle,
  Clock,
} from "lucide-react";

import { Header } from "@/components/layout/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { useDashboard } from "@/hooks/usePayroll";
import type { EmployeeType } from "@/types/employee";

function money(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

function StatCard({
  label,
  value,
  icon: Icon,
  hint,
}: {
  label: string;
  value: string | number;
  icon: React.ComponentType<{
    className?: string;
    style?: React.CSSProperties;
  }>;
  hint?: string;
}) {
  return (
    <Card>
      <CardContent className="flex items-start justify-between gap-3 pt-1">
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="mt-1 text-2xl font-semibold">{value}</p>
          {hint && (
            <p className="mt-0.5 text-xs text-muted-foreground">{hint}</p>
          )}
        </div>
        <div
          className="flex size-9 shrink-0 items-center justify-center rounded-lg"
          style={{ background: "var(--pp-brand-light)" }}
        >
          <Icon className="size-4" style={{ color: "var(--pp-brand)" }} />
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const [employeeType, setEmployeeType] = useState<string>("all");
  const { data, loading, error } = useDashboard(
    employeeType === "all" ? undefined : (employeeType as EmployeeType),
  );

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Dashboard"
        description="Live payroll, headcount and attendance metrics."
        actions={
          <Select value={employeeType} onValueChange={setEmployeeType}>
            <SelectTrigger className="w-44">
              <SelectValue placeholder="Employee type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All employee types</SelectItem>
              <SelectItem value="FULL_TIME">Full time</SelectItem>
              <SelectItem value="PART_TIME">Part time</SelectItem>
              <SelectItem value="CONTRACT">Contract</SelectItem>
              <SelectItem value="INTERN">Intern</SelectItem>
            </SelectContent>
          </Select>
        }
      />

      <div className="flex-1 space-y-4 p-4 sm:p-6">
        {error && <ErrorBanner message={error} />}
        {loading || !data ? (
          <LoadingBanner label="Loading dashboard…" />
        ) : (
          <>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                label="Active employees"
                value={data.active_employees}
                hint={`${data.total_employees} total · ${data.employees_on_leave} on leave`}
                icon={Users}
              />
              <StatCard
                label="Total net paid"
                value={money(Number(data.total_net_paid))}
                hint={`Avg salary ${money(Number(data.average_salary))}`}
                icon={Wallet}
              />
              <StatCard
                label="Current payrun"
                value={data.current_payrun_status ?? "None"}
                hint={
                  data.current_payrun_status
                    ? `Net ${money(Number(data.payroll_total_net))}`
                    : "No payrun yet"
                }
                icon={TrendingUp}
              />
              <StatCard
                label="Pending time off"
                value={data.pending_time_off_requests}
                hint={`${data.approved_time_off_requests} approved`}
                icon={CalendarCheck}
              />
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <Card className="lg:col-span-1">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Clock className="size-4" /> Attendance health
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-semibold">
                    {Number(data.attendance_health).toFixed(1)}%
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {data.present_attendance} present · {data.absent_attendance}{" "}
                    absent of {data.total_attendance_records} records
                  </p>
                  <p className="mt-3 text-xs text-muted-foreground">
                    {data.recent_payslips} payslips generated to date
                  </p>
                </CardContent>
              </Card>

              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <AlertCircle className="size-4" /> Salary cost by department
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {data.department_salary_costs.length === 0 ? (
                    <p className="text-sm text-muted-foreground">
                      No finalized payslips yet — run payroll to see costs here.
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {data.department_salary_costs.map((dept) => (
                        <div
                          key={dept.department_id ?? "unassigned"}
                          className="flex items-center justify-between rounded-lg border px-3 py-2 text-sm"
                        >
                          <span>{dept.department_name}</span>
                          <span className="font-medium">
                            {money(Number(dept.total_salary))}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
