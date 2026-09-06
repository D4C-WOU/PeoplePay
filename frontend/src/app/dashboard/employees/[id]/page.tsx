"use client";

import { useParams } from "next/navigation";

import { Header } from "@/components/layout/header";
import { EmployeeForm } from "@/components/employees/employee-form";
import { useEmployee } from "@/hooks/useEmployees";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";

export default function EditEmployeePage() {
  const params = useParams<{ id: string }>();
  const { data: employee, loading, error } = useEmployee(params.id);

  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header title="Edit employee" description={employee?.employee_number} />
      <div className="pp-page-content flex-1 p-4 sm:p-6">
        <div className="mx-auto max-w-2xl">
          {loading && <LoadingBanner />}
          {error && <ErrorBanner message={error} />}
          {employee && <EmployeeForm employee={employee} />}
        </div>
      </div>
    </div>
  );
}
