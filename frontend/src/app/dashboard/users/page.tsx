import { ShieldAlert } from "lucide-react";

import { Header } from "@/components/layout/header";

export default function UsersPage() {
  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title="User access"
        description="Review the current availability of workspace user administration."
      />
      <div className="pp-page-content flex-1 p-4 sm:p-6">
        <section className="app-surface mx-auto flex max-w-3xl items-start gap-4 p-5 sm:p-7">
          <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-700">
            <ShieldAlert className="size-5" />
          </span>
          <div>
            <h2 className="text-base font-semibold text-[var(--text)]">
              User management API not available
            </h2>
            <p className="mt-2 text-sm leading-6 text-[var(--text-2)]">
              The connected Django API currently exposes role-check endpoints,
              but it does not register a user-list or user-update endpoint. This
              screen stays read-only rather than showing fabricated users or
              sending requests that cannot succeed.
            </p>
            <p className="mt-3 text-sm leading-6 text-[var(--text-2)]">
              User administration can be enabled here once the backend provides
              authenticated user listing and update endpoints. No backend
              changes have been made as part of this frontend pass.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
