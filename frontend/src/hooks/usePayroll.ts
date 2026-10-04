import { apiDownload, apiRequest } from "@/lib/api";
import { useFetch } from "@/hooks/useFetch";
import { paginateItems } from "@/types/pagination";
import type { PaginatedResponse, PaginationParams } from "@/types/pagination";
import type {
  DashboardData,
  Payrun,
  PayrunValidation,
  Payslip,
  SalaryRule,
  SalaryStructure,
} from "@/types/payroll";

type BackendSalaryRule = Omit<SalaryRule, "id" | "salary_structure_id"> & {
  id: number;
  salary_structure: number;
  salary_structure_name?: string;
};

type BackendPayslipLine = {
  id: number;
  salary_rule?: number | null;
  rule_name: string;
  code: string;
  name: string;
  category: string;
  sequence: number;
  base_amount: number;
  calculated_amount: number;
  description?: string | null;
};

type BackendPayslip = Omit<Payslip, "id" | "payrun_id" | "employee_id" | "contract_id" | "salary_structure_id" | "lines" | "employee_number" | "employee_name" | "deductions_amount"> & {
  id: number;
  payrun: number;
  employee: number;
  employee_name: string;
  employee_number: string;
  contract?: number | null;
  salary_structure?: number | null;
  deduction_amount: number;
  lines: BackendPayslipLine[];
};

type BackendPayrun = {
  id: number;
  name: string;
  salary_structure?: number | null;
  salary_structure_name?: string;
  period_start: string;
  period_end: string;
  payment_date?: string | null;
  status: Payrun["status"];
  selected_employees: number[];
  selected_employee_count?: number;
  employee_count: number;
  gross_total: number;
  deduction_total: number;
  net_total: number;
  payslips?: BackendPayslip[];
};

function mapSalaryRule(rule: BackendSalaryRule): SalaryRule {
  return {
    ...rule,
    id: String(rule.id),
    salary_structure_id: String(rule.salary_structure),
    is_active: true,
  };
}

function mapPayslipLine(line: BackendPayslipLine) {
  return {
    ...line,
    id: String(line.id),
    salary_rule_id: line.salary_rule == null ? null : String(line.salary_rule),
    rule_code: line.code,
    rule_name: line.rule_name,
  };
}

function mapPayslip(slip: BackendPayslip): Payslip {
  return {
    ...slip,
    id: String(slip.id),
    payrun_id: String(slip.payrun),
    employee_id: String(slip.employee),
    contract_id: slip.contract == null ? null : String(slip.contract),
    salary_structure_id:
      slip.salary_structure == null ? null : String(slip.salary_structure),
    deductions_amount: Number(slip.deduction_amount ?? 0),
    lines: (slip.lines ?? []).map(mapPayslipLine),
  };
}

function mapPayrun(payrun: BackendPayrun): Payrun {
  return {
    ...payrun,
    id: String(payrun.id),
    salary_structure_id:
      payrun.salary_structure == null ? null : String(payrun.salary_structure),
    employee_ids: (payrun.selected_employees ?? []).map(String),
    total_gross: Number(payrun.gross_total ?? 0),
    total_deductions: Number(payrun.deduction_total ?? 0),
    total_net: Number(payrun.net_total ?? 0),
    payslips: (payrun.payslips ?? []).map(mapPayslip),
    salary_structure: payrun.salary_structure == null ? null : String(payrun.salary_structure),
    selected_employees: (payrun.selected_employees ?? []).map(String),
    gross_total: Number(payrun.gross_total ?? 0),
    deduction_total: Number(payrun.deduction_total ?? 0),
    net_total: Number(payrun.net_total ?? 0),
  };
}

export function useSalaryStructures(activeOnly = false) {
  return useFetch<SalaryStructure[]>(
    () =>
      apiRequest<SalaryStructure[]>("/salary/structures", {
        params: { is_active: activeOnly ? true : undefined },
      }),
    [activeOnly],
  );
}

export function useSalaryRules(structureId?: string) {
  return useFetch<SalaryRule[]>(
    async () => {
      const data = await apiRequest<BackendSalaryRule[]>("/salary/rules", {
        params: { salary_structure: structureId },
      });
      return data.map(mapSalaryRule);
    },
    [structureId],
  );
}

export function usePayruns(status?: string) {
  return useFetch<Payrun[]>(
    async () => {
      const data = await apiRequest<BackendPayrun[]>("/payruns", {
        params: { status },
      });
      return data.map(mapPayrun);
    },
    [status],
  );
}

export function usePaginatedPayruns(params: { status?: string } & PaginationParams) {
  return useFetch<PaginatedResponse<Payrun>>(
    async () => {
      const data = await apiRequest<BackendPayrun[]>("/payruns", {
        params: { status: params.status },
      });
      return paginateItems(data.map(mapPayrun), params.page, params.page_size);
    },
    [params.status, params.page, params.page_size],
  );
}

export function usePayrun(id: string | null) {
  return useFetch<Payrun | null>(
    async () => {
      if (!id) return null;
      const data = await apiRequest<BackendPayrun>(`/payruns/${id}`);
      return mapPayrun(data);
    },
    [id],
  );
}

export function usePayslips(params?: {
  payrun_id?: string;
  employee_id?: string;
  status?: string;
}) {
  return useFetch<Payslip[]>(
    async () => {
      const data = await apiRequest<BackendPayslip[]>("/payslips", {
        params: {
          payrun: params?.payrun_id,
          employee: params?.employee_id,
          status: params?.status,
        },
      });
      return data.map(mapPayslip);
    },
    [params?.payrun_id, params?.employee_id, params?.status],
  );
}

export function usePaginatedPayslips(
  params: { payrun_id?: string; employee_id?: string; status?: string } & PaginationParams,
) {
  return useFetch<PaginatedResponse<Payslip>>(
    async () => {
      const data = await apiRequest<BackendPayslip[]>("/payslips", {
        params: {
          payrun: params.payrun_id,
          employee: params.employee_id,
          status: params.status,
        },
      });
      return paginateItems(data.map(mapPayslip), params.page, params.page_size);
    },
    [params.payrun_id, params.employee_id, params.status, params.page, params.page_size],
  );
}

export function useDashboard() {
  return useFetch<DashboardData>(() => apiRequest<DashboardData>("/dashboard"), []);
}

export const salaryStructureApi = {
  create: (data: Partial<SalaryStructure>) =>
    apiRequest<SalaryStructure>("/salary/structures", { method: "POST", body: data }),
  update: (id: string, data: Partial<SalaryStructure>) =>
    apiRequest<SalaryStructure>(`/salary/structures/${id}`, {
      method: "PATCH",
      body: data,
    }),
};

export const salaryRuleApi = {
  create: (data: Partial<SalaryRule>) => {
    const { salary_structure_id, ...fields } = data;

    return apiRequest<SalaryRule>("/salary/rules", {
      method: "POST",
      body: {
        ...fields,
        salary_structure: salary_structure_id,
      },
    });
  },
  update: (id: string, data: Partial<SalaryRule>) => {
    const { salary_structure_id, ...fields } = data;

    return apiRequest<SalaryRule>(`/salary/rules/${id}`, {
      method: "PATCH",
      body: {
        ...fields,
        ...(salary_structure_id ? { salary_structure: salary_structure_id } : {}),
      },
    });
  },
};

export const payrunApi = {
  create: (data: {
    name?: string;
    period_start: string;
    period_end: string;
    payment_date?: string;
    salary_structure_id: string;
    employee_ids: string[];
  }) =>
    apiRequest<Payrun>("/payruns", {
      method: "POST",
      body: {
        name: data.name,
        period_start: data.period_start,
        period_end: data.period_end,
        payment_date: data.payment_date,
        salary_structure: data.salary_structure_id,
        selected_employees: data.employee_ids,
      },
    }),
  compute: (id: string) =>
    apiRequest<Payrun>(`/payruns/${id}/compute`, { method: "POST" }),
  validate: (id: string) =>
    apiRequest<Payrun>(`/payruns/${id}/validation`),
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
