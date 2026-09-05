export type SalaryRuleCategory =
  | "EARNING"
  | "DEDUCTION"
  | "TAX"
  | "EMPLOYER_CONTRIBUTION";
export type CalculationType = "FIXED" | "PERCENTAGE" | "FORMULA";

export interface SalaryStructure {
  id: string;
  code: string;
  name: string;
  description?: string | null;
  currency: string;
  is_active: boolean;
}

export interface SalaryRule {
  id: string;
  salary_structure_id: string;
  code: string;
  name: string;
  category: SalaryRuleCategory;
  calculation_type: CalculationType;
  amount?: number | null;
  percentage?: number | null;
  formula?: string | null;
  sequence: number;
  is_active: boolean;
}

export type PayrunStatus = "DRAFT" | "PROCESSING" | "COMPLETED" | "CANCELLED";

export interface Payrun {
  id: string;
  period_start: string;
  period_end: string;
  payment_date?: string | null;
  salary_structure_id?: string | null;
  employee_ids: string[];
  status: PayrunStatus;
  employee_count: number;
  total_gross: number;
  total_deductions: number;
  total_tax: number;
  total_net: number;
}

export type PayslipStatus = "DRAFT" | "FINALIZED" | "PAID" | "CANCELLED";

export interface PayslipLine {
  id: string;
  salary_rule_id?: string | null;
  rule_code: string;
  rule_name: string;
  category: string;
  quantity: number;
  rate: number;
  amount: number;
  sequence: number;
}

export interface Payslip {
  id: string;
  payrun_id: string;
  employee_id: string;
  contract_id?: string | null;
  employee_number: string;
  employee_name: string;
  currency: string;
  gross_amount: number;
  deductions_amount: number;
  tax_amount: number;
  net_amount: number;
  status: PayslipStatus;
  generated_at?: string | null;
  lines: PayslipLine[];
}

export interface PayrunValidation {
  payrun_id: string;
  valid: boolean;
  warning_count: number;
  warnings: {
    employee_id: string;
    employee_number: string;
    type: string;
    message: string;
  }[];
}

export interface DepartmentSalaryCost {
  department_id: string | null;
  department_name: string;
  total_salary: number;
}

export interface DashboardData {
  total_employees: number;
  active_employees: number;
  employees_on_leave: number;
  pending_time_off_requests: number;
  approved_time_off_requests: number;
  current_payrun_status: string | null;
  payroll_total_net: number;
  total_net_paid: number;
  average_salary: number;
  total_attendance_records: number;
  present_attendance: number;
  absent_attendance: number;
  attendance_health: number;
  recent_payslips: number;
  department_salary_costs: DepartmentSalaryCost[];
}