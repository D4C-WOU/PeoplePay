import { apiDownload, apiRequest } from "@/lib/api";
import { useFetch } from "@/hooks/useFetch";
import type {
  DashboardData,
  Payrun,
  PayrunValidation,
  Payslip,
  SalaryRule,
  SalaryStructure,
} from "@/types/payroll";
import type { PaginatedResponse, PaginationParams } from "@/types/pagination";

export function useSalaryStructures(activeOnly = false) {
  return useFetch<SalaryStructure[]>(
    () =>
      apiRequest<SalaryStructure[]>("/salary/structures", {
        params: { active_only: activeOnly },
      }),
    [activeOnly]
  );
}

export function useSalaryRules(structureId?: string) {
  return useFetch<SalaryRule[]>(
    () => apiRequest<SalaryRule[]>("/salary/rules", { params: { structure_id: structureId } }),
    [structureId]
  );
}

export function usePayruns(status?: string) {
  return useFetch<Payrun[]>(
    () => apiRequest<Payrun[]>("/payruns", { params: { status } }),
    [status]
  );
}

export function usePaginatedPayruns(
  params: { status?: string } & PaginationParams
) {
  return useFetch<PaginatedResponse<Payrun>>(
    () => apiRequest<PaginatedResponse<Payrun>>("/payruns", { params }),
    [params.status, params.page, params.page_size]
  );
}

export function usePayrun(id: string | null) {
  return useFetch<Payrun | null>(
    () => (id ? apiRequest<Payrun>(`/payruns/${id}`) : Promise.resolve(null)),
    [id]
  );
}

export function usePayslips(params?: { payrun_id?: string; employee_id?: string; status?: string }) {
  return useFetch<Payslip[]>(
    () => apiRequest<Payslip[]>("/payslips", { params }),
    [params?.payrun_id, params?.employee_id, params?.status]
  );
}

export function usePaginatedPayslips(
  params: { payrun_id?: string; employee_id?: string; status?: string } & PaginationParams
) {
  return useFetch<PaginatedResponse<Payslip>>(
    () => apiRequest<PaginatedResponse<Payslip>>("/payslips", { params }),
    [
      params.payrun_id,
      params.employee_id,
      params.status,
      params.page,
      params.page_size,
    ]
  );
}

export function useDashboard(employeeType?: string) {
  return useFetch<DashboardData>(
    () => apiRequest<DashboardData>("/dashboard", { params: { employee_type: employeeType } }),
    [employeeType]
  );
}

export const salaryStructureApi = {
  create: (data: Partial<SalaryStructure>) =>
    apiRequest<SalaryStructure>("/salary/structures", { method: "POST", body: data }),
  update: (id: string, data: Partial<SalaryStructure>) =>
    apiRequest<SalaryStructure>(`/salary/structures/${id}`, { method: "PATCH", body: data }),
};

export const salaryRuleApi = {
  create: (data: Partial<SalaryRule>) =>
    apiRequest<SalaryRule>("/salary/rules", { method: "POST", body: data }),
  update: (id: string, data: Partial<SalaryRule>) =>
    apiRequest<SalaryRule>(`/salary/rules/${id}`, { method: "PATCH", body: data }),
};

export const payrunApi = {
  create: (data: {
    period_start: string;
    period_end: string;
    payment_date?: string;
    salary_structure_id: string;
    employee_ids: string[];
  }) => apiRequest<Payrun>("/payruns", { method: "POST", body: data }),
  validate: (id: string) => apiRequest<PayrunValidation>(`/payruns/${id}/validation`),
  process: (id: string) => apiRequest<Payrun>(`/payruns/${id}/process`, { method: "POST" }),
  finalize: (id: string) => apiRequest<Payrun>(`/payruns/${id}/finalize`, { method: "POST" }),
  cancel: (id: string) => apiRequest<Payrun>(`/payruns/${id}/cancel`, { method: "POST" }),
  sendPayslips: (id: string) =>
    apiRequest<{ total: number; sent: number; failed: number }>(
      `/payruns/${id}/send-payslips`,
      { method: "POST" }
    ),
};

export const payslipApi = {
  downloadPdf: async (id: string, filename: string) => {
    const blob = await apiDownload(`/payslips/${id}/pdf`);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};
