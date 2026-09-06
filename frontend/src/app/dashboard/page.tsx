"use client";

import { useState } from "react";
import Link from "next/link";
import {
  AlertCircle,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Building2,
  CalendarCheck,
  CheckCircle2,
  Clock3,
  FileText,
  Plus,
  Users,
  Wallet,
} from "lucide-react";

import { useDashboard } from "@/hooks/usePayroll";
import { useAuth } from "@/hooks/useAuth";
import { useAttendance, attendanceApi } from "@/hooks/useAttendance";
import {
  useTimeOffRequests,
  useTimeOffTypes,
  timeOffApi,
} from "@/hooks/useTimeOff";
import { LoadingBanner } from "@/components/shared/state-banner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { StatusBadge } from "@/components/shared/status-badge";

function money(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

function pct(value: number) {
  return `${Number(value ?? 0).toFixed(1)}%`;
}

function StatCard({
  label,
  value,
  detail,
  icon: Icon,
  tone,
  href,
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: React.ElementType;
  tone: "teal" | "clay" | "gold" | "blue";
  href: string;
}) {
  return (
    <Link href={href} className={`dashboard-stat dashboard-stat-${tone}`}>
      <div className="dashboard-stat-top">
        <span className="dashboard-stat-icon">
          <Icon />
        </span>
        <ArrowUpRight className="dashboard-stat-arrow" />
      </div>
      <div>
        <span className="dashboard-stat-label">{label}</span>
        <strong className="dashboard-stat-value">{value}</strong>
        <span className="dashboard-stat-detail">{detail}</span>
      </div>
    </Link>
  );
}

function SectionTitle({
  label,
  title,
  href,
}: {
  label: string;
  title: string;
  href?: string;
}) {
  return (
    <div className="dashboard-section-title">
      <div>
        <span>{label}</span>
        <h2>{title}</h2>
      </div>
      {href && (
        <Link href={href}>
          View all <ArrowRight />
        </Link>
      )}
    </div>
  );
}

function localDate() {
  const date = new Date();
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 10);
}

function EmployeeDashboard() {
  const today = localDate();
  const {
    data: attendance,
    loading: attendanceLoading,
    reload: reloadAttendance,
  } = useAttendance();
  const {
    data: requests,
    loading: requestsLoading,
    reload: reloadRequests,
  } = useTimeOffRequests();
  const { data: timeOffTypes } = useTimeOffTypes(true);
  const [savingAttendance, setSavingAttendance] = useState(false);
  const [savingLeave, setSavingLeave] = useState(false);
  const [attendanceError, setAttendanceError] = useState<string | null>(null);
  const [leaveError, setLeaveError] = useState<string | null>(null);
  const [typeId, setTypeId] = useState("");
  const [startDate, setStartDate] = useState(today);
  const [endDate, setEndDate] = useState(today);
  const [reason, setReason] = useState("");

  const todayRecord = attendance?.find(
    (record) => record.attendance_date === today,
  );
  const recentRequests = (requests ?? []).slice(0, 4);

  async function markAttendance() {
    setSavingAttendance(true);
    setAttendanceError(null);
    try {
      if (todayRecord?.check_in && !todayRecord.check_out) {
        await attendanceApi.update(todayRecord.id, {
          check_out: new Date().toISOString(),
        });
      } else if (!todayRecord) {
        await attendanceApi.create({
          employee_id: "",
          attendance_date: today,
          check_in: new Date().toISOString(),
          expected_hours: 8,
          status: "PRESENT",
        });
      }
      reloadAttendance();
    } catch (error) {
      setAttendanceError(
        error instanceof ApiError
          ? error.message
          : "Could not update attendance.",
      );
    } finally {
      setSavingAttendance(false);
    }
  }

  async function requestLeave(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingLeave(true);
    setLeaveError(null);
    try {
      await timeOffApi.createRequest({
        employee_id: "",
        time_off_type_id: typeId,
        start_date: startDate,
        end_date: endDate,
        reason: reason || undefined,
      });
      setReason("");
      reloadRequests();
    } catch (error) {
      setLeaveError(
        error instanceof ApiError
          ? error.message
          : "Could not submit leave request.",
      );
    } finally {
      setSavingLeave(false);
    }
  }

  return (
    <div className="dashboard-page dashboard-self-service-page">
      <section className="dashboard-hero">
        <div className="dashboard-hero-inner">
          <div>
            <span className="dashboard-date">Self-service</span>
            <h1>Keep your day up to date.</h1>
            <p>Mark attendance and submit leave requests from one place.</p>
          </div>
        </div>
      </section>
      <div className="dashboard-page-inner space-y-6">
        <section className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
          <div className="dashboard-panel flex flex-col justify-between gap-6">
            <div>
              <span className="dashboard-section-title">
                <span>Today</span>
              </span>
              <h2 className="mt-1 text-xl font-semibold">Attendance</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {todayRecord?.check_out
                  ? "Your attendance is complete for today."
                  : todayRecord?.check_in
                    ? "You are checked in. Mark check-out when you finish."
                    : "You have not marked attendance yet."}
              </p>
            </div>
            <Button
              onClick={markAttendance}
              disabled={
                attendanceLoading ||
                savingAttendance ||
                !!todayRecord?.check_out
              }
            >
              {attendanceLoading || savingAttendance
                ? "Loading..."
                : todayRecord?.check_in
                  ? "Mark check-out"
                  : "Mark attendance"}
            </Button>
            {attendanceError && (
              <p className="text-sm text-destructive">{attendanceError}</p>
            )}
          </div>

          <form
            onSubmit={requestLeave}
            className="dashboard-panel flex flex-col gap-4"
          >
            <div>
              <span className="dashboard-section-title">
                <span>Time off</span>
              </span>
              <h2 className="mt-1 text-xl font-semibold">Request leave</h2>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="flex flex-col gap-2">
                <Label>Leave type</Label>
                <select
                  className="h-9 rounded-xl border border-(--pp-border-strong) bg-white px-3 text-sm"
                  value={typeId}
                  onChange={(event) => setTypeId(event.target.value)}
                  required
                >
                  <option value="">Select type</option>
                  {timeOffTypes?.map((type) => (
                    <option key={type.id} value={type.id}>
                      {type.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="employee-leave-start">From</Label>
                <Input
                  id="employee-leave-start"
                  type="date"
                  value={startDate}
                  onChange={(event) => setStartDate(event.target.value)}
                  required
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="employee-leave-end">To</Label>
                <Input
                  id="employee-leave-end"
                  type="date"
                  value={endDate}
                  onChange={(event) => setEndDate(event.target.value)}
                  min={startDate}
                  required
                />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="employee-leave-reason">Reason</Label>
              <Textarea
                id="employee-leave-reason"
                value={reason}
                onChange={(event) => setReason(event.target.value)}
                placeholder="Add a short reason (optional)"
              />
            </div>
            <div className="flex items-center justify-between gap-3">
              {leaveError ? (
                <p className="text-sm text-destructive">{leaveError}</p>
              ) : (
                <span />
              )}
              <Button type="submit" disabled={savingLeave || !typeId}>
                {savingLeave ? "Submitting..." : "Submit request"}
              </Button>
            </div>
          </form>
        </section>

        <section className="dashboard-panel">
          <div className="dashboard-section-title">
            <div>
              <span>History</span>
              <h2>Recent leave requests</h2>
            </div>
          </div>
          {requestsLoading ? (
            <LoadingBanner label="Loading leave requests..." />
          ) : recentRequests.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No leave requests yet.
            </p>
          ) : (
            <div className="mt-4 grid gap-2">
              {recentRequests.map((request) => (
                <div
                  key={request.id}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-(--pp-border) p-3"
                >
                  <div>
                    <p className="font-medium">
                      {request.start_date} to {request.end_date}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {request.requested_days} day(s)
                    </p>
                  </div>
                  <StatusBadge status={request.status} />
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function DashboardContent() {
  const { user } = useAuth();
  const { data, loading } = useDashboard();

  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
  const name = user?.email?.split("@")[0] ?? "there";
  const date = new Intl.DateTimeFormat("en-IN", {
    weekday: "long",
    month: "long",
    day: "numeric",
  }).format(new Date());

  const departments = [...(data?.department_salary_costs ?? [])]
    .sort((a, b) => b.total_salary - a.total_salary)
    .slice(0, 6);
  const largestDepartment = departments[0]?.total_salary || 1;

  return (
    <div className="dashboard-page dashboard-admin-page">
      <section className="dashboard-hero">
        <div className="dashboard-hero-inner">
          <div>
            <span className="dashboard-date">{date}</span>
            <h1>
              {greeting}, {name}.
            </h1>
            <p>
              Here’s your people operations at a glance. Focus on the items that
              need attention today.
            </p>
          </div>
          <div className="dashboard-hero-actions">
            <Link
              href="/dashboard/employees/new"
              className="dashboard-primary-action"
            >
              <Plus /> Add employee
            </Link>
            <Link
              href="/dashboard/payroll/payruns"
              className="dashboard-secondary-action"
            >
              <Wallet /> Run payroll
            </Link>
          </div>
        </div>
      </section>

      <div className="dashboard-page-inner">
        {loading && !data ? (
          <LoadingBanner label="Preparing your workspace…" />
        ) : (
          <>
            <section>
              <SectionTitle
                label="Workforce pulse"
                title="Today in PeoplePay"
              />
              <div className="dashboard-stat-grid">
                <StatCard
                  label="Total employees"
                  value={data?.total_employees ?? 0}
                  detail={`${data?.active_employees ?? 0} active right now`}
                  icon={Users}
                  tone="teal"
                  href="/dashboard/employees"
                />
                <StatCard
                  label="On leave"
                  value={data?.employees_on_leave ?? 0}
                  detail={`${data?.pending_time_off_requests ?? 0} requests waiting`}
                  icon={CalendarCheck}
                  tone="gold"
                  href="/dashboard/time-off"
                />
                <StatCard
                  label="Attendance health"
                  value={pct(data?.attendance_health ?? 0)}
                  detail={`${data?.present_attendance ?? 0} present today`}
                  icon={Clock3}
                  tone="clay"
                  href="/dashboard/attendance"
                />
                <StatCard
                  label="Net payroll paid"
                  value={money(data?.total_net_paid ?? 0)}
                  detail="Most recent finalized run"
                  icon={Wallet}
                  tone="blue"
                  href="/dashboard/payroll"
                />
              </div>
            </section>

            <div className="dashboard-main-grid">
              <section className="dashboard-panel">
                <div className="dashboard-panel-header">
                  <SectionTitle
                    label="Payroll snapshot"
                    title="Cost by department"
                  />
                </div>
                <div className="dashboard-departments">
                  {departments.length ? (
                    departments.map((department) => (
                      <div
                        className="dashboard-department"
                        key={department.department_name}
                      >
                        <span className="dashboard-department-icon">
                          <Building2 />
                        </span>
                        <div className="dashboard-department-body">
                          <div className="dashboard-department-meta">
                            <strong>{department.department_name}</strong>
                            <span>{money(department.total_salary)}</span>
                          </div>
                          <div className="dashboard-progress">
                            <span
                              style={{
                                width: `${(department.total_salary / largestDepartment) * 100}%`,
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="dashboard-empty-row">
                      Department salary data will appear here once payroll is
                      active.
                    </div>
                  )}
                </div>
              </section>

              <section className="dashboard-panel dashboard-review-panel">
                <SectionTitle
                  label="Needs attention"
                  title="Review queue"
                  href="/dashboard/time-off/requests"
                />
                <div className="dashboard-review-list">
                  <Link
                    href="/dashboard/time-off/requests"
                    className="dashboard-review-item is-warning"
                  >
                    <span className="dashboard-review-icon">
                      <AlertCircle />
                    </span>
                    <span>
                      <strong>Time-off requests</strong>
                      <small>
                        {data?.pending_time_off_requests ?? 0} pending approval
                      </small>
                    </span>
                    <ArrowUpRight />
                  </Link>
                  <div className="dashboard-review-item">
                    <span className="dashboard-review-icon">
                      <CheckCircle2 />
                    </span>
                    <span>
                      <strong>Approved leave</strong>
                      <small>
                        {data?.approved_time_off_requests ?? 0} requests this
                        period
                      </small>
                    </span>
                  </div>
                  <div className="dashboard-review-item">
                    <span className="dashboard-review-icon">
                      <FileText />
                    </span>
                    <span>
                      <strong>Recent payslips</strong>
                      <small>
                        {data?.recent_payslips ?? 0} generated recently
                      </small>
                    </span>
                  </div>
                </div>
              </section>
            </div>

            <section>
              <SectionTitle label="Shortcuts" title="Move work forward" />
              <div className="dashboard-shortcuts">
                {[
                  [
                    "Add employee",
                    "Onboard a new hire",
                    "/dashboard/employees/new",
                    Users,
                  ],
                  [
                    "Review leave",
                    "Approve pending requests",
                    "/dashboard/time-off/requests",
                    CalendarCheck,
                  ],
                  [
                    "Open attendance",
                    "Review today’s records",
                    "/dashboard/attendance",
                    Clock3,
                  ],
                  [
                    "View payslips",
                    "Find a generated payslip",
                    "/dashboard/payroll/payslips",
                    BarChart3,
                  ],
                ].map(([label, detail, href, Icon]) => {
                  const ShortcutIcon = Icon as React.ElementType;
                  return (
                    <Link
                      href={href as string}
                      key={href as string}
                      className="dashboard-shortcut"
                    >
                      <span>
                        <ShortcutIcon />
                      </span>
                      <span>
                        <strong>{label as string}</strong>
                        <small>{detail as string}</small>
                      </span>
                      <ArrowRight />
                    </Link>
                  );
                })}
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  return user?.role === "EMPLOYEE" ? (
    <EmployeeDashboard />
  ) : (
    <DashboardContent />
  );
}
