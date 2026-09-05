import type { LucideIcon } from "lucide-react";

export function EmptyState({
  icon: Icon,
  title,
  description,
}: {
  icon: LucideIcon;
  title: string;
  description?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-[var(--pp-border-strong)] bg-white px-6 py-16 text-center">
      <div className="flex size-13 items-center justify-center rounded-2xl bg-[var(--pp-brand-light)]">
        <Icon className="size-6 text-[var(--pp-brand)]" />
      </div>
      <p className="font-semibold text-slate-900">{title}</p>
      {description && (
        <p className="max-w-sm text-sm text-slate-500">{description}</p>
      )}
    </div>
  );
}
