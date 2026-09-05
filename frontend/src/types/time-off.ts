export type TimeOffStatus = "PENDING" | "APPROVED" | "REJECTED" | "CANCELLED";

export interface TimeOffType {
  id: string;
  code: string;
  name: string;
  description?: string | null;
  default_allocation: number;
  is_paid: boolean;
  is_active: boolean;
}

export interface TimeOffAllocation {
  id: string;
  employee_id: string;
  time_off_type_id: string;
  year: number;
  allocated_days: number;
  used_days: number;
}

export interface TimeOffRequest {
  id: string;
  employee_id: string;
  time_off_type_id: string;
  start_date: string;
  end_date: string;
  requested_days: number;
  reason?: string | null;
  status: TimeOffStatus;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
}