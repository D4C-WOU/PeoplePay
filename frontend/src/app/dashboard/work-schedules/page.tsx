"use client";

import { useState } from "react";
import { CalendarDays } from "lucide-react";

import { Header } from "@/components/layout/header";
import { DataTable } from "@/components/shared/data-table";
import { FilterBar } from "@/components/shared/filter-bar";
import { StatusBadge } from "@/components/shared/status-badge";
import { useSchedules } from "@/hooks/useEmployees";

export default function WorkSchedulesPage() {
  const { data: schedules, loading, error } = useSchedules();
  const [query, setQuery] = useState("");
  const rows = (schedules ?? []).filter((schedule) =>
    schedule.name.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title="Work schedules"
        description="Define the working patterns used by contracts and attendance operations."
      />
      <div className="pp-page-content flex-1 space-y-4 p-4 sm:p-6">
        <FilterBar
          search={query}
          onSearchChange={setQuery}
          searchPlaceholder="Search schedules"
          hasActiveFilters={Boolean(query)}
          onClear={() => setQuery("")}
        />
        <DataTable
          rows={rows}
          rowKey={(schedule) => schedule.id}
          loading={loading}
          error={error}
          emptyIcon={CalendarDays}
          emptyTitle="No work schedules yet"
          emptyDescription="Work schedules will appear here once they are configured in the system."
          columns={[
            {
              key: "name",
              header: "Schedule",
              render: (schedule) => (
                <span className="font-medium">{schedule.name}</span>
              ),
            },
            {
              key: "hours",
              header: "Weekly hours",
              render: (schedule) =>
                `${Number(schedule.total_weekly_hours).toFixed(1)} hours`,
            },
            {
              key: "days",
              header: "Working days",
              render: (schedule) =>
                schedule.days.filter((day) => day.start_time && day.end_time)
                  .length,
            },
            {
              key: "status",
              header: "Status",
              render: (schedule) => (
                <StatusBadge
                  status={schedule.is_active ? "ACTIVE" : "INACTIVE"}
                />
              ),
            },
          ]}
        />
      </div>
    </div>
  );
}
