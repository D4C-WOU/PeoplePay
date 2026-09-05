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
  work_schedule_id?: string | null;
  attendance_date: string;
  check_in?: string | null;
  check_out?: string | null;
  expected_hours: number;
  worked_hours: number;
  overtime_hours: number;
  status: AttendanceStatus;
  notes?: string | null;
}