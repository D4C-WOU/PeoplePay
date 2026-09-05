import { apiRequest } from "@/lib/api";
import { useFetch } from "@/hooks/useFetch";
import type { AttendanceRecord } from "@/types/attendance";
import type { PaginatedResponse, PaginationParams } from "@/types/pagination";

export function useAttendance(params?: {
  employee_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
}) {
  return useFetch<AttendanceRecord[]>(
    () => apiRequest<AttendanceRecord[]>("/attendance", { params }),
    [params?.employee_id, params?.status, params?.start_date, params?.end_date]
  );
}

export function usePaginatedAttendance(params: {
  employee_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
} & PaginationParams) {
  return useFetch<PaginatedResponse<AttendanceRecord>>(
    () => apiRequest<PaginatedResponse<AttendanceRecord>>("/attendance", { params }),
    [
      params.employee_id,
      params.status,
      params.start_date,
      params.end_date,
      params.page,
      params.page_size,
    ]
  );
}

export const attendanceApi = {
  create: (data: Partial<AttendanceRecord>) =>
    apiRequest<AttendanceRecord>("/attendance", { method: "POST", body: data }),
  update: (id: string, data: Partial<AttendanceRecord>) =>
    apiRequest<AttendanceRecord>(`/attendance/${id}`, { method: "PATCH", body: data }),
};
