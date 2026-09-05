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
