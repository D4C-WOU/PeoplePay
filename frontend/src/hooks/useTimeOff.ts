import { apiRequest } from "@/lib/api";
import { useFetch } from "@/hooks/useFetch";
import type {
  TimeOffAllocation,
  TimeOffRequest,
  TimeOffType,
} from "@/types/time-off";

export function useTimeOffTypes(activeOnly = false) {
  return useFetch<TimeOffType[]>(
    () => apiRequest<TimeOffType[]>("/time-off/types", { params: { active_only: activeOnly } }),
    [activeOnly]
  );
}

export function useAllocations(params?: { employee_id?: string; year?: number }) {
  return useFetch<TimeOffAllocation[]>(
    () => apiRequest<TimeOffAllocation[]>("/time-off/allocations", { params }),
    [params?.employee_id, params?.year]
  );
}

export function useTimeOffRequests(params?: { employee_id?: string; status?: string }) {
  return useFetch<TimeOffRequest[]>(
    () => apiRequest<TimeOffRequest[]>("/time-off/requests", { params }),
    [params?.employee_id, params?.status]
  );
}

export const timeOffApi = {
  createType: (data: Partial<TimeOffType>) =>
    apiRequest<TimeOffType>("/time-off/types", { method: "POST", body: data }),
  createAllocation: (data: Partial<TimeOffAllocation>) =>
    apiRequest<TimeOffAllocation>("/time-off/allocations", { method: "POST", body: data }),
  createRequest: (data: Partial<TimeOffRequest>) =>
    apiRequest<TimeOffRequest>("/time-off/requests", { method: "POST", body: data }),
  approve: (id: string) =>
    apiRequest<TimeOffRequest>(`/time-off/requests/${id}/approve`, { method: "POST" }),
  reject: (id: string) =>
    apiRequest<TimeOffRequest>(`/time-off/requests/${id}/reject`, { method: "POST" }),
  cancel: (id: string) =>
    apiRequest<TimeOffRequest>(`/time-off/requests/${id}/cancel`, { method: "POST" }),
};