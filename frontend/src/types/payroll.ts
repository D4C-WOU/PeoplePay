export type SalaryRuleCategory =
  | "BASIC"
  | "ALLOWANCE"
  | "GROSS"
  | "DEDUCTION"
  | "NET";
export type CalculationType = "FIXED" | "PERCENTAGE" | "FORMULA";

export interface SalaryStructure {
  id: string;
  code: string;
  name: string;
  description?: string | null;
  currency: string;
  is_active: boolean;
  rule_count?: number;
}

export interface SalaryRule {
  id: string;
  salary_structure_id: string;
  salary_structure_name?: string;
  code: string;
  name: string;
  category: SalaryRuleCategory;
  calculation_type: CalculationType;
  amount?: number | null;
  percentage?: number | null;
  formula?: string | null;
  sequence: number;
  is_active?: boolean;
}

export type PayrunStatus =
  | "DRAFT"
  | "COMPUTED"
  | "VALIDATED"
  | "PAID"
  | "CANCELLED";

export interface Payrun {
  id: string;
  name: string;
  period_start: string;
  period_end: string;
  payment_date?: string | null;
  salary_structure_id?: string | null;
  salary_structure_name?: string;
  employee_ids: string[];
  status: PayrunStatus;
  employee_count: number;
  total_gross: number;
  total_deductions: number;
  total_net: number;
  payslips?: Payslip[];
  // Backend field aliases kept here because some existing presentation code
  // still uses the names from the Django serializer directly.
  salary_structure?: string | null;
  selected_employees?: string[];
  gross_total?: number;
  deduction_total?: number;
  net_total?: number;
}

export type PayslipStatus = "DRAFT" | "FINALIZED" | "PAID" | "CANCELLED";

export interface PayslipLine {
  id: string;
  salary_rule_id?: string | null;
  rule_code: string;
  rule_name: string;
  code?: string;
  name?: string;
  category: string;
  sequence: number;
  base_amount: number;
  calculated_amount: number;
  description?: string | null;
}

export interface Payslip {
  id: string;
  payrun_id: string;
  employee_id: string;
  employee_number: string;
  employee_name: string;
  contract_id?: string | null;
  salary_structure_id?: string | null;
  salary_structure_name?: string;
  period_start: string;
  period_end: string;
  worked_days: number;
  currency: string;
  gross_amount: number;
  deductions_amount: number;
  net_amount: number;
  status: PayslipStatus;
  generated_at?: string | null;
  lines: PayslipLine[];
}

export interface PayrunValidation {
  payrun_id?: string;
  valid?: boolean;
  warning_count?: number;
  warnings: Array<
    | string
    | {
        employee_id?: string;
        employee_number?: string;
        type?: string;
        message?: string;
      }
  >;
}

export interface DashboardData {
  employees: {
    total: number;
    active: number;
    on_leave: number;
  };
  payroll: {
    total_net_paid: number;
    payslips_generated: number;
    average_salary: number;
  };
  attendance: {
    total: number;
    present: number;
    absent: number;
    half_day: number;
    late: number;
    on_leave: number;
    health_percentage: number;
  };
  time_off: {
    approved: number;
    pending: number;
    rejected: number;
  };
  departments: Array<{
    id: number | string;
    name: string;
    employee_count: number;
    active_employee_count: number;
  }>;
  monthly_salary_trend: Array<Record<string, unknown>>;
}
