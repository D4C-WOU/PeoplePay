import Link from "next/link";
import { ArrowRight, Calculator, Layers3 } from "lucide-react";

import { Header } from "@/components/layout/header";

const salaryAreas = [
  {
    title: "Salary structures",
    description:
      "Define reusable compensation structures for different employee groups.",
    href: "/dashboard/salary/structures",
    icon: Layers3,
  },
  {
    title: "Salary rules",
    description:
      "Configure earnings, deductions, and calculation rules used by payroll.",
    href: "/dashboard/salary/rules",
    icon: Calculator,
  },
];

export default function SalaryPage() {
  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title="Salary"
        description="Manage the structures and rules that power your payroll calculations."
        eyebrow="Payroll setup"
      />
      <div className="mx-auto grid w-full max-w-[1440px] flex-1 grid-cols-1 gap-4 p-5 sm:grid-cols-2 sm:p-8">
        {salaryAreas.map(({ title, description, href, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className="app-surface group flex min-h-44 flex-col justify-between p-5 transition hover:-translate-y-0.5 hover:border-[var(--pp-brand)] hover:shadow-[var(--pp-shadow-sm)]"
          >
            <span className="flex size-10 items-center justify-center rounded-lg bg-[var(--pp-brand-light)] text-[var(--pp-brand)]">
              <Icon className="size-5" />
            </span>
            <span>
              <span className="flex items-center justify-between gap-3 text-base font-semibold text-[var(--text)]">
                {title}
                <ArrowRight className="size-4 text-[var(--pp-brand)] transition group-hover:translate-x-1" />
              </span>
              <span className="mt-1 block max-w-sm text-sm text-[var(--text-2)]">
                {description}
              </span>
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
