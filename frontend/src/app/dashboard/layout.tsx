"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import {
  Bell,
  ChevronRight,
  LogOut,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  X,
} from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import {
  ROLE_LABELS,
  canAccessHR,
  canAccessPayroll,
  canAccessSalary,
  canAccessTimeAttendance,
} from "@/lib/auth";
import { NAV_ITEMS } from "@/lib/navigation";

function NavItem({
  item,
  pathname,
  collapsed,
  onNavigate,
}: {
  item: (typeof NAV_ITEMS)[0];
  pathname: string;
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const isActive = item.exact
    ? pathname === item.href
    : pathname.startsWith(item.href) && item.href !== "/dashboard";
  const childActive = item.children?.some((child) =>
    pathname.startsWith(child.href),
  );
  const Icon = item.icon;
  const active = isActive || childActive;

  return (
    <li>
      <Link
        href={item.href}
        onClick={onNavigate}
        title={collapsed ? item.label : undefined}
        className={`dashboard-nav-item${active ? " is-active" : ""}${collapsed ? " is-collapsed" : ""}`}
      >
        <Icon className="size-4.25 shrink-0" />
        <span className={collapsed ? "sr-only" : ""}>{item.label}</span>
        {!collapsed && item.children?.length ? (
          <ChevronRight
            className={`dashboard-nav-chevron${active ? " is-open" : ""}`}
          />
        ) : null}
      </Link>

      {item.children?.length && !collapsed && active ? (
        <ul className="dashboard-subnav">
          {item.children.map((child) => {
            const selected = pathname.startsWith(child.href);
            return (
              <li key={child.href}>
                <Link
                  href={child.href}
                  onClick={onNavigate}
                  className={`dashboard-subnav-item${selected ? " is-active" : ""}`}
                >
                  <span className="dashboard-subnav-line" />
                  {child.label}
                </Link>
              </li>
            );
          })}
        </ul>
      ) : null}
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

  useEffect(() => {
    const restrictedForPayroll =
      pathname.startsWith("/dashboard/attendance") ||
      pathname.startsWith("/dashboard/time-off") ||
      pathname.startsWith("/dashboard/work-schedules");

    if (restrictedForPayroll && !canAccessTimeAttendance(user?.role)) {
      router.replace("/dashboard");
    }
  }, [pathname, router, user?.role]);

  const visibleItems = useMemo(
    () =>
      NAV_ITEMS.filter((item) => {
        if (["/dashboard/settings", "/dashboard/users"].includes(item.href)) {
          return user?.role === "ADMIN";
        }
        if (item.href === "/dashboard/payroll") {
          return canAccessPayroll(user?.role);
        }
        if (item.href === "/dashboard/salary") {
          return canAccessSalary(user?.role);
        }
        if (
          [
            "/dashboard/employees",
            "/dashboard/contracts",
            "/dashboard/departments",
          ].includes(item.href)
        ) {
          return canAccessHR(user?.role) || user?.role === "MANAGER";
        }
        if (item.href === "/dashboard/work-schedules") {
          return user?.role === "ADMIN";
        }
        if (
          ["/dashboard/attendance", "/dashboard/time-off"].includes(item.href)
        ) {
          return canAccessTimeAttendance(user?.role);
        }
        if (item.href === "/dashboard/payroll/payslips") {
          return user?.role === "EMPLOYEE";
        }
        return true;
      }),
    [user?.role],
  );

  const currentLabel =
    pathname === "/dashboard"
      ? "Overview"
      : (pathname
          .split("/")
          .filter(Boolean)
          .slice(-1)[0]
          ?.replaceAll("-", " ") ?? "Workspace");

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="dashboard-loading-card">
          <span className="dashboard-logo">P3</span>
          <span className="dashboard-loading-dot" />
          <span>Loading workspace…</span>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="dashboard-shell">
      {sidebarOpen && (
        <button
          aria-label="Close navigation"
          className="dashboard-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`dashboard-sidebar${sidebarCollapsed ? " is-collapsed" : ""}${sidebarOpen ? " is-mobile-open" : ""}`}
      >
        <div className="dashboard-sidebar-top">
          <Link
            href="/dashboard"
            className="dashboard-brand"
            onClick={() => setSidebarOpen(false)}
          >
            <span className="dashboard-brand-mark">P3</span>
            <span className={sidebarCollapsed ? "sr-only" : ""}>
              <strong>PeoplePay360</strong>
              <small>HR &amp; Payroll ops</small>
            </span>
          </Link>

          <button
            className="dashboard-sidebar-toggle"
            aria-label={
              sidebarCollapsed ? "Expand navigation" : "Collapse navigation"
            }
            onClick={() => setSidebarCollapsed((value) => !value)}
          >
            {sidebarCollapsed ? <PanelLeftOpen /> : <PanelLeftClose />}
          </button>

          <button
            className="dashboard-mobile-close"
            aria-label="Close navigation"
            onClick={() => setSidebarOpen(false)}
          >
            <X />
          </button>
        </div>

        <nav className="dashboard-nav">
          {visibleItems.map((item, index) => (
            <div key={item.href}>
              {!sidebarCollapsed &&
                (index === 0 ||
                  item.group !== visibleItems[index - 1].group) && (
                  <p className="dashboard-nav-group">{item.group}</p>
                )}
              <NavItem
                item={item}
                pathname={pathname}
                collapsed={sidebarCollapsed}
                onNavigate={() => setSidebarOpen(false)}
              />
            </div>
          ))}
        </nav>

        <div className="dashboard-account">
          <div className="dashboard-account-main">
            <span className="dashboard-avatar">
              {user.email[0].toUpperCase()}
            </span>
            <span className={sidebarCollapsed ? "sr-only" : "min-w-0"}>
              <strong>{user.email.split("@")[0]}</strong>
              <small>{ROLE_LABELS[user.role]}</small>
            </span>
          </div>
          <button
            onClick={logout}
            className="dashboard-signout"
            title={sidebarCollapsed ? "Sign out" : undefined}
          >
            <LogOut />
            <span className={sidebarCollapsed ? "sr-only" : ""}>Sign out</span>
          </button>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-topbar">
          <button
            className="dashboard-menu-button"
            aria-label="Open navigation"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu />
          </button>

          <div className="dashboard-breadcrumb">
            <span>Workspace</span>
            <ChevronRight />
            <strong>{currentLabel}</strong>
          </div>

          <div className="dashboard-topbar-actions">
            <button aria-label="Search" title="Search">
              <Search />
            </button>
            <button aria-label="Notifications" title="Notifications">
              <Bell />
            </button>
            <span className="dashboard-topbar-avatar">
              {user.email[0].toUpperCase()}
            </span>
          </div>
        </header>

        <div
          className={`dashboard-content dashboard-route-${pathname.replace(/\//g, "-").replace(/^-|-$/g, "") || "overview"}`}
        >
          {children}
        </div>
      </main>
    </div>
  );
}
