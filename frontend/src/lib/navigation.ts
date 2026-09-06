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
  { group: "People", label: "Overview", href: "/dashboard", icon: LayoutGrid, exact: true },
  { group: "People", label: "Employees", href: "/dashboard/employees", icon: Users2 },
  { group: "People", label: "Contracts", href: "/dashboard/contracts", icon: FileSignature },
  { group: "People", label: "Departments", href: "/dashboard/departments", icon: Building2 },
  { group: "Time & attendance", label: "Attendance", href: "/dashboard/attendance", icon: Clock4 },
  { group: "Time & attendance", label: "Time Off", href: "/dashboard/time-off", icon: CalendarDays },
  { group: "Time & attendance", label: "Work Schedules", href: "/dashboard/work-schedules", icon: CalendarClock },
  { group: "My workspace", label: "My Payslips", href: "/dashboard/payroll/payslips", icon: Wallet },
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
  { group: "System", label: "Settings", href: "/dashboard/settings", icon: Settings },
  { group: "System", label: "Users", href: "/dashboard/users", icon: ShieldCheck },
];
