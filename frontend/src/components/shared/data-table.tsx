import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";

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
  if (loading && !rows.length)
    return <LoadingBanner label="Loading records…" />;
  if (error && !rows.length) return <ErrorBanner message={error} />;
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
    <div className={`data-table-shell${loading ? " is-refreshing" : ""}`}>
      {error && (
        <div className="data-table-inline-error">
          <ErrorBanner message={error} />
        </div>
      )}
      <div className="data-table-scroll">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((column) => (
                <TableHead key={column.key} className={column.className}>
                  {column.header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow
                key={rowKey(row)}
                className={onRowClick ? "data-row-clickable" : undefined}
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
      </div>

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
