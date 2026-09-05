"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { ROLE_LABELS, canAccessHR, canAccessPayroll } from "@/lib/auth";
import {
  Menu,
  X,
  LogOut,
  ChevronRight,
  Bell,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  LayoutGrid,
  Users2,
  FileSignature,
  Building2,
  Clock4,
  CalendarDays,
  CalendarClock,
  Wallet,
  BarChart3,
  Settings as SettingsIcon,
  ShieldCheck,
} from "lucide-react";

const NAV_ITEMS = [
  {
    group: "People",
    label: "Overview",
    href: "/dashboard",
    icon: LayoutGrid,
    exact: true,
  },
  {
    group: "People",
    label: "Employees",
    href: "/dashboard/employees",
    icon: Users2,
  },
  {
    group: "People",
    label: "Contracts",
    href: "/dashboard/contracts",
    icon: FileSignature,
  },
  {
    group: "People",
    label: "Departments",
    href: "/dashboard/departments",
    icon: Building2,
  },
  {
    group: "Time & attendance",
    label: "Attendance",
    href: "/dashboard/attendance",
    icon: Clock4,
  },
  {
    group: "Time & attendance",
    label: "Time Off",
    href: "/dashboard/time-off",
    icon: CalendarDays,
  },
  {
    group: "Time & attendance",
    label: "Work Schedules",
    href: "/dashboard/work-schedules",
    icon: CalendarClock,
  },
  {
    group: "Payroll",
    label: "Payroll",
    href: "/dashboard/payroll",
    icon: Wallet,
    children: [
      { label: "Pay Runs", href: "/dashboard/payroll/payruns" },
      { label: "Payslips", href: "/dashboard/payroll/payslips" },
    ],
  },
  {
    group: "Payroll",
    label: "Salary",
    href: "/dashboard/salary",
    icon: BarChart3,
    children: [
      { label: "Structures", href: "/dashboard/salary/structures" },
      { label: "Rules", href: "/dashboard/salary/rules" },
    ],
  },
  {
    group: "System",
    label: "Settings",
    href: "/dashboard/settings",
    icon: SettingsIcon,
  },
  {
    group: "System",
    label: "Users",
    href: "/dashboard/users",
    icon: ShieldCheck,
  },
];

function NavItem({
  item,
  pathname,
  collapsed,
}: {
  item: (typeof NAV_ITEMS)[0];
  pathname: string;
  collapsed: boolean;
}) {
  const isActive = item.exact
    ? pathname === item.href
    : pathname.startsWith(item.href) && item.href !== "/dashboard";
  const hasChildren = item.children && item.children.length > 0;
  const childActive = item.children?.some((c) => pathname.startsWith(c.href));
  const Icon = item.icon;
  const active = isActive || childActive;

  return (
    <li>
      <Link
        href={item.href}
        className="group relative flex items-center gap-2.5 rounded-xl px-3 py-2 text-[13px] font-medium transition-colors"
        style={{
          color: active ? "white" : "var(--pp-sidebar-fg)",
          background: active ? "var(--pp-sidebar-active)" : "transparent",
        }}
        onMouseEnter={(e) => {
          if (!active)
            (e.currentTarget as HTMLElement).style.background =
              "var(--pp-sidebar-hover)";
        }}
        onMouseLeave={(e) => {
          if (!active)
            (e.currentTarget as HTMLElement).style.background = "transparent";
        }}
      >
        <Icon
          className="size-4 shrink-0"
          style={{ opacity: active ? 1 : 0.65 }}
        />
        <span className={collapsed ? "sr-only" : ""}>{item.label}</span>
      </Link>
      {hasChildren && !collapsed && active && (
        <ul
          className="mt-0.5 ml-[26px] space-y-0.5 border-l pl-3.5"
          style={{ borderColor: "var(--pp-sidebar-border)" }}
        >
          {item.children!.map((child) => {
            const ca = pathname.startsWith(child.href);
            return (
              <li key={child.href}>
                <Link
                  href={child.href}
                  className="block rounded-lg px-2.5 py-1.5 text-xs transition-colors"
                  style={{
                    color: ca ? "white" : "var(--pp-sidebar-fg)",
                    background: ca ? "rgba(255,255,255,.08)" : "transparent",
                  }}
                >
                  {child.label}
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </li>
  );
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[var(--pp-page-bg)]">
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span className="size-2 animate-pulse rounded-full bg-[var(--pp-brand)]" />
          Loading workspace…
        </div>
      </div>
    );
  }
  if (!user) return null;

  const visibleItems = NAV_ITEMS.filter((item) => {
    if (["/dashboard/settings", "/dashboard/users"].includes(item.href))
      return user.role === "ADMIN";
    if (["/dashboard/payroll", "/dashboard/salary"].includes(item.href))
      return canAccessPayroll(user.role);
    if (
      [
        "/dashboard/employees",
        "/dashboard/contracts",
        "/dashboard/departments",
      ].includes(item.href)
    )
      return (
        canAccessHR(user.role) ||
        canAccessPayroll(user.role) ||
        user.role === "MANAGER"
      );
    return true;
  });

  return (
    <div className="flex h-screen overflow-hidden">
      {sidebarOpen && (
        <button
          aria-label="Close navigation"
          className="fixed inset-0 z-30 bg-slate-950/40 backdrop-blur-[2px] md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex flex-col overflow-y-auto app-scrollbar transition-[width,transform] duration-200 md:static md:z-auto md:translate-x-0 ${sidebarCollapsed ? "md:w-[76px]" : "md:w-64"} w-64 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}
        style={{
          background:
            "linear-gradient(180deg, var(--pp-sidebar-bg-2) 0%, var(--pp-sidebar-bg) 60%)",
        }}
      >
        <div
          className={`flex items-center justify-between gap-2.5 border-b px-4 py-4.5 ${sidebarCollapsed ? "md:px-3" : ""}`}
          style={{ borderColor: "var(--pp-sidebar-border)" }}
        >
          <div className="flex items-center gap-2.5">
            <div
              className="flex size-9 shrink-0 items-center justify-center rounded-xl text-xs font-bold text-white shadow-[var(--pp-shadow-sm)]"
              style={{
                background:
                  "linear-gradient(135deg, var(--pp-brand), var(--pp-accent))",
              }}
            >
              P3
            </div>
            <div className={sidebarCollapsed ? "md:hidden" : ""}>
              <p className="text-sm font-semibold leading-tight text-white">
                PeoplePay360
              </p>
              <p className="text-[11px] text-white/40">HR & Payroll ops</p>
            </div>
          </div>
          <button
            className="text-white/50 md:hidden"
            aria-label="Close navigation"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="size-5" />
          </button>
          <button
            className="hidden text-white/40 hover:text-white md:block"
            aria-label={
              sidebarCollapsed ? "Expand navigation" : "Collapse navigation"
            }
            onClick={() => setSidebarCollapsed((v) => !v)}
          >
            {sidebarCollapsed ? (
              <PanelLeftOpen className="size-4" />
            ) : (
              <PanelLeftClose className="size-4" />
            )}
          </button>
        </div>

        <nav className="flex-1 px-2.5 py-3.5">
          <ul className="space-y-0.5">
            {visibleItems.map((item, index) => (
              <div key={item.href}>
                {!sidebarCollapsed &&
                  (index === 0 ||
                    item.group !== visibleItems[index - 1].group) && (
                    <p className="mb-1.5 mt-4.5 px-3 text-[10px] font-semibold uppercase tracking-[0.14em] text-white/25 first:mt-0">
                      {item.group}
                    </p>
                  )}
                <NavItem
                  item={item}
                  pathname={pathname}
                  collapsed={sidebarCollapsed}
                />
              </div>
            ))}
          </ul>
        </nav>

        <div
          className={`border-t px-3 py-3.5 ${sidebarCollapsed ? "md:px-2" : ""}`}
          style={{ borderColor: "var(--pp-sidebar-border)" }}
        >
          <div className="mb-2 flex items-center gap-2.5 rounded-xl px-1.5 py-1.5">
            <div
              className="flex size-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold text-white"
              style={{
                background:
                  "linear-gradient(135deg, var(--pp-accent), var(--pp-brand))",
              }}
            >
              {user.email[0].toUpperCase()}
            </div>
            <div className={sidebarCollapsed ? "md:hidden" : "min-w-0"}>
              <p className="truncate text-xs font-medium text-white">
                {user.email.split("@")[0]}
              </p>
              <p className="truncate text-[11px] text-white/40">
                {ROLE_LABELS[user.role]}
              </p>
            </div>
          </div>
          <button
            onClick={logout}
            className={`flex w-full items-center gap-2 rounded-lg px-1.5 py-1.5 text-left text-xs text-white/40 transition hover:bg-white/5 hover:text-white ${sidebarCollapsed ? "md:justify-center" : ""}`}
            title={sidebarCollapsed ? "Sign out" : undefined}
          >
            <LogOut className="size-3.5" />
            <span className={sidebarCollapsed ? "md:hidden" : ""}>
              Sign out
            </span>
          </button>
        </div>
      </aside>

      <main
        className="flex min-w-0 flex-1 flex-col overflow-auto app-scrollbar"
        style={{ background: "var(--pp-page-bg)" }}
      >
        <div className="sticky top-0 z-20 flex h-14 items-center justify-between border-b bg-white/95 px-4 backdrop-blur md:hidden">
          <button
            aria-label="Open navigation"
            className="text-slate-600"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="size-5" />
          </button>
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
            <span className="flex size-7 items-center justify-center rounded-lg bg-[var(--pp-brand)] text-[10px] font-bold text-white">
              P3
            </span>
            PeoplePay360
          </div>
          <span className="size-5" />
        </div>
        <div className="hidden items-center justify-between border-b bg-white/80 px-6 py-2.5 text-xs text-slate-500 backdrop-blur md:flex">
          <div className="flex items-center gap-2">
            <span className="font-medium text-slate-700">Workspace</span>
            <ChevronRight className="size-3 text-slate-300" />
            <span className="font-medium text-slate-900">
              {pathname === "/dashboard"
                ? "Overview"
                : pathname
                    .split("/")
                    .filter(Boolean)
                    .slice(-1)[0]
                    ?.replaceAll("-", " ")}
            </span>
          </div>
          <div className="flex items-center gap-3 text-slate-400">
            <Search className="size-4 cursor-pointer hover:text-slate-600" />
            <Bell className="size-4 cursor-pointer hover:text-slate-600" />
          </div>
        </div>
        <div className="page-enter flex flex-1 flex-col">{children}</div>
      </main>
    </div>
  );
}
