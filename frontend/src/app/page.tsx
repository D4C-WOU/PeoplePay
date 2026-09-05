"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

import { getToken } from "@/lib/auth";

export default function Root() {
  const router = useRouter();

  useEffect(() => {
    router.replace(getToken() ? "/dashboard" : "/login");
  }, [router]);

  return (
    <main className="grid min-h-screen place-items-center bg-[var(--pp-page-bg)]">
      <div className="flex items-center gap-3 rounded-2xl border border-[var(--pp-border)] bg-white px-4 py-3 text-sm text-[var(--text-2)] shadow-[var(--pp-shadow-xs)]">
        <span className="grid size-8 place-items-center rounded-xl bg-[var(--pp-brand-light)] text-xs font-extrabold text-[var(--pp-brand)]">
          P3
        </span>
        <Loader2 className="size-4 animate-spin text-[var(--pp-brand)]" />
        Loading workspace…
      </div>
    </main>
  );
}
