"use client";

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
import { LoadingBanner } from "@/components/shared/state-banner";

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

export default function DashboardPage() {
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
    <div className="dashboard-page">
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
