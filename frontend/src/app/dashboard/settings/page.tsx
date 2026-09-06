import { Header } from "@/components/layout/header";

export default function SettingsPage() {
  return (
    <div className="flex flex-1 flex-col">
      <Header title="Settings" description="Account and workspace settings." />
      <div className="flex-1 p-4 sm:p-6">
        <div className="mx-auto flex min-h-[260px] w-full max-w-2xl items-center justify-center rounded-2xl border border-dashed border-[var(--pp-border-strong)] bg-white px-6 py-16 text-center shadow-[var(--pp-shadow-xs)]">
          <p className="max-w-md text-sm text-muted-foreground">
            Settings are not yet configurable from this screen.
          </p>
        </div>
      </div>
    </div>
  );
}
