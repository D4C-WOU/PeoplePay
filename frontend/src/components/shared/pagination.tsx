"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";

type PaginationProps = {
  page: number;
  pageSize: number;
  total: number;
  pages: number;
  onPageChange: (page: number) => void;
};

export function Pagination({
  page,
  pageSize,
  total,
  pages,
  onPageChange,
}: PaginationProps) {
  if (total <= pageSize && page <= 1) return null;

  const start = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, total);

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-[var(--pp-border)] bg-slate-50/60 px-4 py-3 text-sm text-slate-500">
      <span>
        Showing{" "}
        <span className="font-medium text-slate-700">
          {start}-{end}
        </span>{" "}
        of <span className="font-medium text-slate-700">{total}</span>
      </span>
      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          aria-label="Previous page"
        >
          <ChevronLeft className="size-4" />
        </Button>
        <span className="min-w-20 text-center">
          Page {page} of {Math.max(pages, 1)}
        </span>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={pages === 0 || page >= pages}
          onClick={() => onPageChange(page + 1)}
          aria-label="Next page"
        >
          <ChevronRight className="size-4" />
        </Button>
      </div>
    </div>
  );
}
