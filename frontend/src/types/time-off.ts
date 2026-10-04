export type TimeOffStatus = "PENDING" | "APPROVED" | "REJECTED" | "CANCELLED";

export interface TimeOffType {
  id: string;
  code: string;
  name: string;
  description?: string | null;
  unit: string;
  requires_allocation: boolean;
  requires_approval: boolean;
  affects_payroll: boolean;
  is_active: boolean;
}

export interface TimeOffAllocation {
  id: string;
  employee_id: string;
  employee_name?: string;
  time_off_type_id: string;
  time_off_type_name?: string;
  year?: number;
  allocated_days: number;
  used_days: number;
  remaining_days?: number;
  valid_from?: string | null;
  valid_to?: string | null;
  status?: string;
}

export interface TimeOffRequest {
  id: string;
  employee_id: string;
  employee_name?: string;
  time_off_type_id: string;
  time_off_type_name?: string;
  start_date: string;
  end_date: string;
  requested_days: number;
  reason?: string | null;
  status: TimeOffStatus;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  created_at?: string;
}
