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
    <div className="empty-state flex flex-col items-center justify-center gap-3 border border-dashed border-[var(--pp-border-strong)] bg-white px-6 py-14 text-center">
      <div className="flex size-11 items-center justify-center rounded-lg bg-[var(--pp-brand-light)]">
        <Icon className="size-5 text-[var(--pp-brand)]" />
      </div>
      <p className="font-semibold text-[var(--text)]">{title}</p>
      {description && (
        <p className="max-w-sm text-sm text-[var(--text-2)]">{description}</p>
      )}
    </div>
  );
}
