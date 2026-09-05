import type { ReactNode } from "react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { EmptyState } from "@/components/shared/empty-state";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { Pagination } from "@/components/shared/pagination";
import type { LucideIcon } from "lucide-react";

type DataTableColumn<T> = {
  key: string;
  header: string;
  className?: string;
  render: (row: T) => ReactNode;
};

type DataTableProps<T> = {
  columns: DataTableColumn<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  loading?: boolean;
  error?: string | null;
  emptyTitle: string;
  emptyDescription: string;
  emptyIcon: LucideIcon;
  page?: number;
  pageSize?: number;
  total?: number;
  pages?: number;
  onPageChange?: (page: number) => void;
  onRowClick?: (row: T) => void;
};

export function DataTable<T>({
  columns,
  rows,
  rowKey,
  loading = false,
  error,
  emptyTitle,
  emptyDescription,
  emptyIcon,
  page,
  pageSize,
  total,
  pages,
  onPageChange,
  onRowClick,
}: DataTableProps<T>) {
  if (loading) return <LoadingBanner label="Loading records..." />;
  if (error) return <ErrorBanner message={error} />;
  if (!rows.length) {
    return (
      <EmptyState
        icon={emptyIcon}
        title={emptyTitle}
        description={emptyDescription}
      />
    );
  }

  return (
    <div className="app-surface overflow-hidden">
      <Table>
        <TableHeader className="bg-slate-50/90">
          <TableRow>
            {columns.map((column) => (
              <TableHead
                key={column.key}
                className={`text-[11px] font-semibold uppercase tracking-wide text-slate-500 ${column.className ?? ""}`}
              >
                {column.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow
              key={rowKey(row)}
              className={
                onRowClick
                  ? "cursor-pointer transition-colors hover:bg-[var(--pp-brand-soft)]"
                  : undefined
              }
              onClick={onRowClick ? () => onRowClick(row) : undefined}
              tabIndex={onRowClick ? 0 : undefined}
              onKeyDown={
                onRowClick
                  ? (event) => {
                      if (event.key === "Enter" || event.key === " ")
                        onRowClick(row);
                    }
                  : undefined
              }
            >
              {columns.map((column) => (
                <TableCell key={column.key} className={column.className}>
                  {column.render(row)}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {page !== undefined &&
        pageSize !== undefined &&
        total !== undefined &&
        pages !== undefined &&
        onPageChange && (
          <Pagination
            page={page}
            pageSize={pageSize}
            total={total}
            pages={pages}
            onPageChange={onPageChange}
          />
        )}
    </div>
  );
}

export type { DataTableColumn };
