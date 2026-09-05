"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";

const NAV_ITEMS = [
  {
    label: "Overview",
    href: "/dashboard",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <rect x="3" y="3" width="7" height="7" />
        <rect x="14" y="3" width="7" height="7" />
        <rect x="14" y="14" width="7" height="7" />
        <rect x="3" y="14" width="7" height="7" />
      </svg>
    ),
    exact: true,
  },
  {
    label: "Employees",
    href: "/dashboard/employees",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    ),
  },
  {
    label: "Contracts",
    href: "/dashboard/contracts",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
      </svg>
    ),
  },
  {
    label: "Attendance",
    href: "/dashboard/attendance",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
      </svg>
    ),
  },
  {
    label: "Time Off",
    href: "/dashboard/time-off",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <circle cx="12" cy="12" r="10" />
        <polyline points="12 6 12 12 16 14" />
      </svg>
    ),
  },
  {
    label: "Payroll",
    href: "/dashboard/payroll",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <line x1="12" y1="1" x2="12" y2="23" />
        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
      </svg>
    ),
    children: [
      { label: "Pay Runs", href: "/dashboard/payroll/payruns" },
      { label: "Payslips", href: "/dashboard/payroll/payslips" },
    ],
  },
  {
    label: "Salary",
    href: "/dashboard/salary",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
    children: [
      { label: "Structures", href: "/dashboard/salary/structures" },
      { label: "Rules", href: "/dashboard/salary/rules" },
    ],
  },
  {
    label: "Settings",
    href: "/dashboard/settings",
    icon: (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
      </svg>
    ),
  },
];

function NavItem({
  item,
  pathname,
}: {
  item: (typeof NAV_ITEMS)[0];
  pathname: string;
}) {
  const isActive = item.exact
    ? pathname === item.href
    : pathname.startsWith(item.href) && item.href !== "/dashboard";
  const hasChildren = item.children && item.children.length > 0;
  const childActive = item.children?.some((c) => pathname.startsWith(c.href));

  return (
    <li>
      <Link
        href={item.href}
        className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors"
        style={{
          color: isActive || childActive ? "white" : "var(--pp-sidebar-fg)",
          background: isActive
            ? "var(--pp-brand)"
            : childActive
              ? "rgba(255,255,255,.08)"
              : "transparent",
        }}
        onMouseEnter={(e) => {
          if (!isActive)
            (e.currentTarget as HTMLElement).style.background =
              "var(--pp-sidebar-hover)";
        }}
        onMouseLeave={(e) => {
          if (!isActive)
            (e.currentTarget as HTMLElement).style.background = childActive
              ? "rgba(255,255,255,.08)"
              : "transparent";
        }}
      >
        <span style={{ opacity: isActive || childActive ? 1 : 0.65 }}>
          {item.icon}
        </span>
        <span>{item.label}</span>
      </Link>
      {hasChildren && (childActive || isActive) && (
        <ul className="mt-0.5 ml-6 space-y-0.5">
          {item.children!.map((child) => {
            const ca = pathname.startsWith(child.href);
            return (
              <li key={child.href}>
                <Link
                  href={child.href}
                  className="block px-3 py-1.5 rounded text-xs transition-colors"
                  style={{
                    color: ca ? "white" : "var(--pp-sidebar-fg)",
                    background: ca ? "rgba(255,255,255,.12)" : "transparent",
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

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-sm text-gray-400">Loading…</div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside
        className="w-56 flex flex-col flex-shrink-0 overflow-y-auto"
        style={{ background: "var(--pp-sidebar-bg)" }}
      >
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-4 py-4 border-b border-white/10">
          <div
            className="w-7 h-7 rounded flex items-center justify-center text-white font-bold text-xs flex-shrink-0"
            style={{ background: "var(--pp-brand)" }}
          >
            P3
          </div>
          <div>
            <p className="text-white text-sm font-semibold leading-tight">
              PeoplePay360
            </p>
            <p className="text-gray-500 text-xs">HR & Payroll</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-2 py-3">
          <ul className="space-y-0.5">
            {NAV_ITEMS.map((item) => (
              <NavItem key={item.href} item={item} pathname={pathname} />
            ))}
          </ul>
        </nav>

        {/* User */}
        <div className="px-3 py-3 border-t border-white/10">
          <div className="flex items-center gap-2 mb-2">
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-semibold flex-shrink-0"
              style={{ background: "var(--pp-brand)" }}
            >
              {user.email[0].toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-white text-xs font-medium truncate">
                {user.email.split("@")[0]}
              </p>
              <p className="text-gray-500 text-xs truncate">
                {user.role.replace("_", " ")}
              </p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full text-left text-xs text-gray-500 hover:text-gray-300 transition-colors px-1 py-1"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main
        className="flex-1 overflow-auto"
        style={{ background: "var(--pp-page-bg)" }}
      >
        {children}
      </main>
    </div>
  );
}
