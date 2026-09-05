"use client";

import { useState } from "react";
import { CalendarClock, Plus } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { StatusBadge } from "@/components/shared/status-badge";
import { DataTable } from "@/components/shared/data-table";
import { FilterBar } from "@/components/shared/filter-bar";
import { usePaginatedAttendance, attendanceApi } from "@/hooks/useAttendance";
import { useEmployees } from "@/hooks/useEmployees";
import { ApiError } from "@/lib/api";
import type { AttendanceStatus } from "@/types/attendance";

const PAGE_SIZE = 10;

function NewAttendanceDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const { data: employees } = useEmployees();
  const [employeeId, setEmployeeId] = useState("");
  const [attendanceDate, setAttendanceDate] = useState("");
  const [checkIn, setCheckIn] = useState("");
  const [checkOut, setCheckOut] = useState("");
  const [expectedHours, setExpectedHours] = useState("8");
  const [status, setStatus] = useState<AttendanceStatus>("PRESENT");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await attendanceApi.create({
        employee_id: employeeId,
        attendance_date: attendanceDate,
        check_in: checkIn ? `${attendanceDate}T${checkIn}:00` : null,
        check_out: checkOut ? `${attendanceDate}T${checkOut}:00` : null,
        expected_hours: Number(expectedHours),
        status,
      });
      setOpen(false);
      setEmployeeId("");
      setAttendanceDate("");
      setCheckIn("");
      setCheckOut("");
      onCreated();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not create attendance record.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        <Plus /> New record
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New attendance record</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="space-y-1.5">
            <Label>Employee</Label>
            <Select value={employeeId} onValueChange={setEmployeeId}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select employee" />
              </SelectTrigger>
              <SelectContent>
                {employees?.map((emp) => (
                  <SelectItem key={emp.id} value={emp.id}>
                    {emp.first_name} {emp.last_name} ({emp.employee_number})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="date">Date</Label>
            <Input
              id="date"
              type="date"
              value={attendanceDate}
              onChange={(e) => setAttendanceDate(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="checkin">Check in</Label>
              <Input
                id="checkin"
                type="time"
                value={checkIn}
                onChange={(e) => setCheckIn(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="checkout">Check out</Label>
              <Input
                id="checkout"
                type="time"
                value={checkOut}
                onChange={(e) => setCheckOut(e.target.value)}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="expected">Expected hours</Label>
              <Input
                id="expected"
                type="number"
                step="0.5"
                min={0}
                value={expectedHours}
                onChange={(e) => setExpectedHours(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Status</Label>
              <Select
                value={status}
                onValueChange={(v) => setStatus(v as AttendanceStatus)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="PRESENT">Present</SelectItem>
                  <SelectItem value="ABSENT">Absent</SelectItem>
                  <SelectItem value="HALF_DAY">Half day</SelectItem>
                  <SelectItem value="LATE">Late</SelectItem>
                  <SelectItem value="ON_LEAVE">On leave</SelectItem>
                  <SelectItem value="HOLIDAY">Holiday</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          {error && (
            <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </p>
          )}
          <DialogFooter>
            <DialogClose render={<Button variant="outline" type="button" />}>
              Cancel
            </DialogClose>
            <Button
              type="submit"
              disabled={saving || !employeeId || !attendanceDate}
            >
              {saving ? "Saving…" : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function AttendancePage() {
  const [status, setStatus] = useState<string>("all");
  const [page, setPage] = useState(1);
  const { data: employees } = useEmployees();
  const {
    data: attendancePage,
    loading,
    error,
    reload,
  } = usePaginatedAttendance({
    status: status === "all" ? undefined : status,
    page,
    page_size: PAGE_SIZE,
  });
  const records = attendancePage?.items ?? [];

  const employeeName = (id: string) => {
    const emp = employees?.find((e) => e.id === id);
    return emp ? `${emp.first_name} ${emp.last_name}` : id;
  };

  function updateStatus(value: string) {
    setStatus(value);
    setPage(1);
  }

  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title="Attendance"
        description="Check-ins, check-outs, and worked hours across the team."
        actions={<NewAttendanceDialog onCreated={reload} />}
      />
      <div className="pp-page-content flex-1 space-y-4 p-4 sm:p-6">
        <FilterBar
          hasActiveFilters={status !== "all"}
          onClear={() => updateStatus("all")}
        >
          <Select value={status} onValueChange={updateStatus}>
            <SelectTrigger className="w-44 bg-white">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              <SelectItem value="PRESENT">Present</SelectItem>
              <SelectItem value="ABSENT">Absent</SelectItem>
              <SelectItem value="HALF_DAY">Half day</SelectItem>
              <SelectItem value="LATE">Late</SelectItem>
              <SelectItem value="ON_LEAVE">On leave</SelectItem>
              <SelectItem value="HOLIDAY">Holiday</SelectItem>
            </SelectContent>
          </Select>
        </FilterBar>
        <DataTable
          rows={records}
          rowKey={(record) => record.id}
          loading={loading}
          error={error}
          emptyIcon={CalendarClock}
          emptyTitle="No attendance records"
          emptyDescription="Add a record, or wait for employees to check in."
          page={attendancePage?.page}
          pageSize={attendancePage?.page_size}
          total={attendancePage?.total}
          pages={attendancePage?.pages}
          onPageChange={setPage}
          columns={[
            {
              key: "employee",
              header: "Employee",
              render: (record) => (
                <span className="font-medium">
                  {employeeName(record.employee_id)}
                </span>
              ),
            },
            {
              key: "date",
              header: "Date",
              render: (record) => record.attendance_date,
            },
            {
              key: "in",
              header: "Check in",
              render: (record) =>
                record.check_in
                  ? new Date(record.check_in).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "—",
            },
            {
              key: "out",
              header: "Check out",
              render: (record) =>
                record.check_out
                  ? new Date(record.check_out).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "—",
            },
            {
              key: "worked",
              header: "Worked",
              render: (record) => `${record.worked_hours}h`,
            },
            {
              key: "overtime",
              header: "Overtime",
              render: (record) => `${record.overtime_hours}h`,
            },
            {
              key: "status",
              header: "Status",
              render: (record) => <StatusBadge status={record.status} />,
            },
          ]}
        />
      </div>
    </div>
  );
}
