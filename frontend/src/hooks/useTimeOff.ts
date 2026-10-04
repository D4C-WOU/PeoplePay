import { apiRequest } from "@/lib/api";
import { useFetch } from "@/hooks/useFetch";
import type { TimeOffAllocation, TimeOffRequest, TimeOffType } from "@/types/time-off";

type BackendAllocation = Omit<TimeOffAllocation, "id" | "employee_id" | "time_off_type_id" | "used_days"> & {
  id: number;
  employee: number;
  time_off_type: number;
  taken_days: number;
};

type BackendRequest = Omit<TimeOffRequest, "id" | "employee_id" | "time_off_type_id" | "requested_days"> & {
  id: number;
  employee: number;
  time_off_type: number;
  duration_days: number;
};

function mapAllocation(item: BackendAllocation): TimeOffAllocation {
  return {
    ...item,
    id: String(item.id),
    employee_id: String(item.employee),
    time_off_type_id: String(item.time_off_type),
    used_days: Number(item.taken_days ?? 0),
    allocated_days: Number(item.allocated_days ?? 0),
    remaining_days: Number(item.remaining_days ?? item.allocated_days - item.taken_days),
    year: item.valid_from ? new Date(item.valid_from).getFullYear() : undefined,
  };
}

function mapRequest(item: BackendRequest): TimeOffRequest {
  return {
    ...item,
    id: String(item.id),
    employee_id: String(item.employee),
    time_off_type_id: String(item.time_off_type),
    requested_days: Number(item.duration_days ?? 0),
  };
}

export function useTimeOffTypes(activeOnly = false) {
  return useFetch<TimeOffType[]>(
    () => apiRequest<TimeOffType[]>("/time-off/types", { params: { is_active: activeOnly ? true : undefined } }),
    [activeOnly],
  );
}

export function useAllocations(params?: { employee_id?: string; year?: number }) {
  return useFetch<TimeOffAllocation[]>(
    async () => {
      const data = await apiRequest<BackendAllocation[]>("/time-off/allocations", {
        params: { employee: params?.employee_id, year: params?.year },
      });
      return data.map(mapAllocation);
    },
    [params?.employee_id, params?.year],
  );
}

export function useTimeOffRequests(params?: { employee_id?: string; status?: string }) {
  return useFetch<TimeOffRequest[]>(
    async () => {
      const data = await apiRequest<BackendRequest[]>("/time-off/requests", {
        params: { employee: params?.employee_id, status: params?.status },
      });
      return data.map(mapRequest);
    },
    [params?.employee_id, params?.status],
  );
}

export const timeOffApi = {
  createType: (data: Partial<TimeOffType>) =>
    apiRequest<TimeOffType>("/time-off/types", { method: "POST", body: data }),
  createAllocation: (data: Partial<TimeOffAllocation>) =>
    apiRequest<TimeOffAllocation>("/time-off/allocations", {
      method: "POST",
      body: {
        employee: data.employee_id,
        time_off_type: data.time_off_type_id,
        allocated_days: data.allocated_days,
        valid_from: data.year ? `${data.year}-01-01` : data.valid_from,
        valid_to: data.year ? `${data.year}-12-31` : data.valid_to,
        status: data.status,
      },
    }),
  createRequest: (data: Partial<TimeOffRequest>) =>
    apiRequest<TimeOffRequest>("/time-off/requests", {
      method: "POST",
      body: {
        employee: data.employee_id,
        time_off_type: data.time_off_type_id,
        start_date: data.start_date,
        end_date: data.end_date,
        reason: data.reason,
      },
    }),
  approve: (id: string) =>
    apiRequest<TimeOffRequest>(`/time-off/requests/${id}/approve`, { method: "POST" }),
  reject: (id: string) =>
    apiRequest<TimeOffRequest>(`/time-off/requests/${id}/reject`, { method: "POST" }),
};


/** Read-only leave history for the currently authenticated employee. */
export function useMyTimeOff() {
  return useFetch<TimeOffRequest[]>(
    async () => {
      const data = await apiRequest<Array<{
        id: number;
        time_off_type: number;
        time_off_type_name?: string;
        start_date: string;
        end_date: string;
        requested_days: number;
        reason?: string | null;
        status: TimeOffRequest["status"];
        reviewed_at?: string | null;
      }>>("/me/time-off");

      return data.map((request) => ({
        ...request,
        id: String(request.id),
        employee_id: "",
        time_off_type_id: String(request.time_off_type),
      }));
    },
    [],
  );
}
