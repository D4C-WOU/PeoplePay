import { Header } from "@/components/layout/header";
import { EmployeeForm } from "@/components/employees/employee-form";

export default function NewEmployeePage() {
  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title="New employee"
        description="Add a new hire to the workforce."
      />
      <div className="pp-page-content flex-1 p-4 sm:p-6">
        <div className="mx-auto max-w-3xl">
          <EmployeeForm />
        </div>
      </div>
    </div>
  );
}
