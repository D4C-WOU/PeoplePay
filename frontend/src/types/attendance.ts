export type AttendanceStatus =
  | "PRESENT"
  | "ABSENT"
  | "HALF_DAY"
  | "LATE"
  | "ON_LEAVE"
  | "HOLIDAY";

export interface AttendanceRecord {
  id: string;
  employee_id: string;
  employee_name?: string;
  work_schedule_id?: string | null;
  work_schedule_name?: string | null;
  attendance_date: string;
  check_in?: string | null;
  check_out?: string | null;
  expected_hours: number;
  worked_hours: number;
  overtime_hours: number;
  status: AttendanceStatus;
  notes?: string | null;
  corrected_by?: string | null;
  corrected_by_name?: string | null;
  corrected_at?: string | null;
}
