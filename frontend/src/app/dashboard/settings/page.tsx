import { Header } from "@/components/layout/header";

export default function SettingsPage() {
  return (
    <div className="flex flex-1 flex-col">
      <Header title="Settings" description="Account and workspace settings." />
      <div className="flex-1 p-4 sm:p-6">
        <p className="text-sm text-muted-foreground">
          Settings are not yet configurable from this screen.
        </p>
      </div>
    </div>
  );
}
