import { apiRequest } from "@/lib/api";
import { useFetch } from "@/hooks/useFetch";
import { paginateItems } from "@/types/pagination";
import type { AttendanceRecord } from "@/types/attendance";
import type { PaginatedResponse, PaginationParams } from "@/types/pagination";

type BackendAttendance = AttendanceRecord & {
  id: number;
  employee: number;
  employee_name?: string;
  work_schedule?: number | null;
  work_schedule_name?: string | null;
};

function mapAttendance(record: BackendAttendance): AttendanceRecord {
  return {
    ...record,
    id: String(record.id),
    employee_id: String(record.employee),
    work_schedule_id:
      record.work_schedule == null ? null : String(record.work_schedule),
  };
}

export function useAttendance(params?: {
  employee_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
}) {
  return useFetch<AttendanceRecord[]>(
    async () => {
      const data = await apiRequest<BackendAttendance[]>("/attendance", {
        params: {
          employee: params?.employee_id,
          status: params?.status,
          start_date: params?.start_date,
          end_date: params?.end_date,
        },
      });
      return data.map(mapAttendance);
    },
    [params?.employee_id, params?.status, params?.start_date, params?.end_date],
  );
}

export function usePaginatedAttendance(params: {
  employee_id?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
} & PaginationParams) {
  return useFetch<PaginatedResponse<AttendanceRecord>>(
    async () => {
      const data = await apiRequest<BackendAttendance[]>("/attendance", {
        params: {
          employee: params.employee_id,
          status: params.status,
          start_date: params.start_date,
          end_date: params.end_date,
        },
      });
      return paginateItems(data.map(mapAttendance), params.page, params.page_size);
    },
    [
      params.employee_id,
      params.status,
      params.start_date,
      params.end_date,
      params.page,
      params.page_size,
    ],
  );
}

export const attendanceApi = {
  create: (data: Partial<AttendanceRecord>) => {
    const { employee_id, work_schedule_id, ...fields } = data;

    return apiRequest<AttendanceRecord>("/attendance", {
      method: "POST",
      body: {
        ...fields,
        employee: employee_id,
        work_schedule: work_schedule_id || null,
      },
    });
  },
  update: (id: string, data: Partial<AttendanceRecord>) => {
    const { employee_id, work_schedule_id, ...fields } = data;

    return apiRequest<AttendanceRecord>(`/attendance/${id}`, {
      method: "PATCH",
      body: {
        ...fields,
        ...(employee_id ? { employee: employee_id } : {}),
        ...(work_schedule_id !== undefined ? { work_schedule: work_schedule_id || null } : {}),
      },
    });
  },
};


/** Read-only attendance history for the currently authenticated employee. */
export function useMyAttendance() {
  return useFetch<AttendanceRecord[]>(
    async () => {
      const data = await apiRequest<Array<{
        id: number;
        attendance_date: string;
        check_in?: string | null;
        check_out?: string | null;
        expected_hours: number;
        worked_hours: number;
        overtime_hours: number;
        status: AttendanceRecord["status"];
        work_schedule?: number | null;
        work_schedule_name?: string | null;
        notes?: string | null;
      }>>("/me/attendance");

      return data.map((record) => ({
        ...record,
        id: String(record.id),
        employee_id: "",
        work_schedule_id: record.work_schedule == null ? null : String(record.work_schedule),
      }));
    },
    [],
  );
}
