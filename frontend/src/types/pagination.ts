export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface PaginationParams {
  [key: string]: string | number | boolean | undefined;
  page?: number;
  page_size?: number;
}

/** Convert a plain Django list into the shape used by the table component. */
export function paginateItems<T>(items: T[], page = 1, pageSize = 10): PaginatedResponse<T> {
  const total = items.length;
  const pages = total === 0 ? 0 : Math.ceil(total / pageSize);
  const safePage = pages === 0 ? 1 : Math.min(Math.max(page, 1), pages);
  const start = (safePage - 1) * pageSize;

  return {
    items: items.slice(start, start + pageSize),
    total,
    page: safePage,
    page_size: pageSize,
    pages,
  };
}
