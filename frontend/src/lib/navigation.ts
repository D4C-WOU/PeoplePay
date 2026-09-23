import {
  BarChart3,
  Building2,
  CalendarClock,
  CalendarDays,
  Clock4,
  FileSignature,
  LayoutGrid,
  Settings,
  ShieldCheck,
  Users2,
  Wallet,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

type NavigationChild = { label: string; href: string };

export type NavigationItem = {
  group: string;
  label: string;
  href: string;
  icon: LucideIcon;
  exact?: boolean;
  children?: readonly NavigationChild[];
};

export const NAV_ITEMS: readonly NavigationItem[] = [
  { group: "Analytics", label: "Dashboard", href: "/dashboard", icon: LayoutGrid, exact: true },
  { group: "Analytics", label: "Reports", href: "/dashboard/reports", icon: BarChart3 },

  { group: "People", label: "Employees", href: "/dashboard/employees", icon: Users2 },
  { group: "People", label: "Attendance", href: "/dashboard/attendance", icon: Clock4 },
  { group: "People", label: "Time Off", href: "/dashboard/time-off", icon: CalendarDays },

  { group: "Payroll", label: "Pay Runs", href: "/dashboard/payroll/payruns", icon: Wallet },
  { group: "Payroll", label: "Payslips", href: "/dashboard/payroll/payslips", icon: Wallet },

  { group: "Configuration", label: "Contracts", href: "/dashboard/contracts", icon: FileSignature },
  { group: "Configuration", label: "Schedules", href: "/dashboard/work-schedules", icon: CalendarClock },
  { group: "Configuration", label: "Salary Structures", href: "/dashboard/salary/structures", icon: BarChart3 },
  { group: "Configuration", label: "Salary Rules", href: "/dashboard/salary/rules", icon: BarChart3 },

  { group: "Settings", label: "Organization", href: "/dashboard/departments", icon: Building2 },
  { group: "Settings", label: "Users & Roles", href: "/dashboard/users", icon: ShieldCheck },
  { group: "Settings", label: "Settings", href: "/dashboard/settings", icon: Settings },
];
