import { AlertTriangle, Loader2 } from "lucide-react";

export function LoadingBanner({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      className="state-banner state-banner-loading"
      role="status"
      aria-live="polite"
    >
      <span className="state-banner-spinner">
        <Loader2 />
      </span>
      <span>{label}</span>
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="state-banner state-banner-error" role="alert">
      <AlertTriangle />
      <span>{message}</span>
    </div>
  );
}
