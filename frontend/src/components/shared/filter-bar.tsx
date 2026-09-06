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
  className?: string;
};

export function FilterBar({
  search,
  onSearchChange,
  searchPlaceholder = "Search records…",
  children,
  onClear,
  hasActiveFilters = false,
}: FilterBarProps) {
  return (
    <div className="filter-bar">
      {onSearchChange && (
        <div className="filter-search">
          <Search />
          <Input
            value={search ?? ""}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder={searchPlaceholder}
            aria-label={searchPlaceholder}
          />
        </div>
      )}
      {children && <div className="filter-controls">{children}</div>}
      {hasActiveFilters && onClear && (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="filter-clear"
          onClick={onClear}
        >
          <X /> Clear
        </Button>
      )}
    </div>
  );
}
