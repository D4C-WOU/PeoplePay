export type EmployeeStatus = "ACTIVE" | "ON_LEAVE" | "TERMINATED";
export type EmployeeType = "FULL_TIME" | "PART_TIME" | "CONTRACT" | "INTERN";

export interface Department {
  id: string;
  name: string;
  code: string;
  description?: string | null;
  is_active: boolean;
}

export interface Employee {
  id: string;
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  date_of_birth?: string | null;
  hire_date: string;
  termination_date?: string | null;
  job_title?: string | null;
  employee_type: EmployeeType;
  status: EmployeeStatus;
  bank_name?: string | null;
  bank_account_number?: string | null;
  bank_ifsc?: string | null;
  address?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  department_id?: string | null;
  manager_id?: string | null;
  user_id?: string | null;
}

export type EmployeeFormValues = Omit<Employee, "id">;

export type ContractType = "FULL_TIME" | "PART_TIME" | "CONTRACT" | "INTERN";
export type ContractStatus = "ACTIVE" | "EXPIRED" | "TERMINATED" | "CANCELLED";

export interface Contract {
  id: string;
  employee_id: string;
  salary_structure_id: string;
  work_schedule_id?: string | null;
  contract_number: string;
  start_date: string;
  end_date?: string | null;
  contract_type: ContractType;
  base_salary: number;
  currency: string;
  status: ContractStatus;
  notes?: string | null;
}

export type DayOfWeek =
  | "MONDAY"
  | "TUESDAY"
  | "WEDNESDAY"
  | "THURSDAY"
  | "FRIDAY"
  | "SATURDAY"
  | "SUNDAY";

export interface WorkScheduleDay {
  id?: string;
  day_of_week: DayOfWeek;
  start_time?: string | null;
  end_time?: string | null;
  break_minutes: number;
}

export interface WorkSchedule {
  id: string;
  name: string;
  description?: string | null;
  days: WorkScheduleDay[];
  is_active: boolean;
  total_weekly_hours: number;
}