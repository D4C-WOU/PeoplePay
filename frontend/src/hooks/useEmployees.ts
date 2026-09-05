import { apiRequest } from "@/lib/api";
import { useFetch } from "@/hooks/useFetch";
import type {
  Contract,
  Department,
  Employee,
  EmployeeFormValues,
  WorkSchedule,
} from "@/types/employee";
import type { PaginatedResponse, PaginationParams } from "@/types/pagination";

export function useEmployees(params?: { department_id?: string; status?: string }) {
  return useFetch<Employee[]>(
    () => apiRequest<Employee[]>("/employees", { params }),
    [params?.department_id, params?.status]
  );
}

export function usePaginatedEmployees(
  params: { department_id?: string; status?: string; q?: string } & PaginationParams
) {
  return useFetch<PaginatedResponse<Employee>>(
    () => apiRequest<PaginatedResponse<Employee>>("/employees", { params }),
    [params.department_id, params.status, params.q, params.page, params.page_size]
  );
}

export function useEmployee(id: string | null) {
  return useFetch<Employee | null>(
    () => (id ? apiRequest<Employee>(`/employees/${id}`) : Promise.resolve(null)),
    [id]
  );
}

export function useDepartments() {
  return useFetch<Department[]>(() => apiRequest<Department[]>("/departments"), []);
}

export function useSchedules() {
  return useFetch<WorkSchedule[]>(() => apiRequest<WorkSchedule[]>("/schedules"), []);
}

export function useContracts(params?: { employee_id?: string; status?: string }) {
  return useFetch<Contract[]>(
    () => apiRequest<Contract[]>("/contracts", { params }),
    [params?.employee_id, params?.status]
  );
}

export function usePaginatedContracts(
  params: { employee_id?: string; status?: string } & PaginationParams
) {
  return useFetch<PaginatedResponse<Contract>>(
    () => apiRequest<PaginatedResponse<Contract>>("/contracts", { params }),
    [params.employee_id, params.status, params.page, params.page_size]
  );
}

export const employeeApi = {
  create: (data: Partial<EmployeeFormValues>) =>
    apiRequest<Employee>("/employees", { method: "POST", body: data }),
  update: (id: string, data: Partial<EmployeeFormValues>) =>
    apiRequest<Employee>(`/employees/${id}`, { method: "PATCH", body: data }),
  terminate: (id: string) =>
    apiRequest<Employee>(`/employees/${id}`, { method: "DELETE" }),
};

export const contractApi = {
  create: (data: Partial<Contract>) =>
    apiRequest<Contract>("/contracts", { method: "POST", body: data }),
  update: (id: string, data: Partial<Contract>) =>
    apiRequest<Contract>(`/contracts/${id}`, { method: "PATCH", body: data }),
  terminate: (id: string) =>
    apiRequest<Contract>(`/contracts/${id}/terminate`, { method: "POST" }),
};

export const departmentApi = {
  create: (data: Partial<Department>) =>
    apiRequest<Department>("/departments", { method: "POST", body: data }),
  update: (id: string, data: Partial<Department>) =>
    apiRequest<Department>(`/departments/${id}`, { method: "PATCH", body: data }),
};
