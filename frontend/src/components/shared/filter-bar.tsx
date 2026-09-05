import type { ReactNode } from "react";
import { Search, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type FilterBarProps = {
  search?: string;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;
  children?: ReactNode;
  onClear?: () => void;
  hasActiveFilters?: boolean;
};

export function FilterBar({
  search,
  onSearchChange,
  searchPlaceholder = "Search records...",
  children,
  onClear,
  hasActiveFilters = false,
}: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-[var(--pp-border)] bg-white p-2 shadow-[var(--pp-shadow-xs)]">
      {onSearchChange && (
        <div className="relative min-w-60 flex-1">
          <Search className="pointer-events-none absolute left-3 top-2.5 size-4 text-slate-400" />
          <Input
            value={search ?? ""}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder={searchPlaceholder}
            className="border-transparent bg-slate-50 pl-9 focus-visible:border-[var(--pp-brand)] focus-visible:bg-white"
          />
        </div>
      )}
      {children}
      {hasActiveFilters && onClear && (
        <Button type="button" variant="ghost" size="sm" onClick={onClear}>
          <X /> Clear filters
        </Button>
      )}
    </div>
  );
}
