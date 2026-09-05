import { Loader2, AlertTriangle } from "lucide-react";

export function LoadingBanner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 rounded-lg border bg-white px-4 py-6 text-sm text-muted-foreground">
      <Loader2 className="size-4 animate-spin" />
      {label}
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
      <AlertTriangle className="size-4 shrink-0" />
      {message}
    </div>
  );
}
