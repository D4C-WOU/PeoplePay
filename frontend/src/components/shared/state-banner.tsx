import { Loader2, AlertTriangle } from "lucide-react";

export function LoadingBanner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2.5 rounded-2xl border border-[var(--pp-border)] bg-white px-4 py-6 text-sm text-slate-500">
      <Loader2 className="size-4 animate-spin text-[var(--pp-brand)]" />
      {label}
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-2.5 rounded-2xl border border-[var(--pp-danger)]/25 bg-[var(--pp-danger-bg)] px-4 py-3 text-sm text-[var(--pp-danger)]">
      <AlertTriangle className="size-4 shrink-0" />
      {message}
    </div>
  );
}
