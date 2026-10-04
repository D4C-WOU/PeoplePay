import { apiRequest } from "@/lib/api";
import { useFetch } from "@/hooks/useFetch";
import { paginateItems } from "@/types/pagination";
import type { PaginatedResponse, PaginationParams } from "@/types/pagination";
import type {
  Contract,
  Department,
  Employee,
  EmployeeFormValues,
  WorkSchedule,
} from "@/types/employee";

type BackendEmployee = {
  id: number;
  employee_number: string;
  user?: number | null;
  first_name: string;
  last_name: string;
  full_name?: string;
  phone?: string | null;
  date_of_birth?: string | null;
  hire_date: string;
  termination_date?: string | null;
  job_title?: string | null;
  department?: number | null;
  department_name?: string | null;
  manager?: number | null;
  manager_name?: string | null;
  work_schedule?: number | null;
  work_schedule_name?: string | null;
  employee_type: Employee["employee_type"];
  status: Employee["status"];
  address?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  bank_name?: string | null;
  bank_account_number?: string | null;
  bank_ifsc?: string | null;
  email?: string;
};

function mapEmployee(employee: BackendEmployee): Employee {
  return {
    ...employee,
    id: String(employee.id),
    user: employee.user == null ? null : String(employee.user),
    department_id: employee.department == null ? null : String(employee.department),
    manager_id: employee.manager == null ? null : String(employee.manager),
    work_schedule_id:
      employee.work_schedule == null ? null : String(employee.work_schedule),
    user_id: employee.user == null ? null : String(employee.user),
    email: employee.email ?? "",
  };
}

type BackendContract = {
  id: number;
  contract_number: string;
  employee: number;
  employee_name?: string;
  salary_structure: number;
  salary_structure_name?: string;
  work_schedule?: number | null;
  work_schedule_name?: string | null;
  start_date: string;
  end_date?: string | null;
  contract_type: Contract["contract_type"];
  base_salary: number;
  currency: string;
  status: Contract["status"];
  notes?: string | null;
};

function mapContract(contract: BackendContract): Contract {
  return {
    ...contract,
    id: String(contract.id),
    employee_id: String(contract.employee),
    salary_structure_id: String(contract.salary_structure),
    work_schedule_id:
      contract.work_schedule == null ? null : String(contract.work_schedule),
  };
}

function mapDepartment(department: Department): Department {
  return { ...department, id: String(department.id) };
}

export function useEmployees(params?: { department_id?: string; status?: string }) {
  return useFetch<Employee[]>(
    async () => {
      const data = await apiRequest<BackendEmployee[]>("/employees", {
        params: {
          department: params?.department_id,
          status: params?.status,
        },
      });
      return data.map(mapEmployee);
    },
    [params?.department_id, params?.status],
  );
}

export function usePaginatedEmployees(
  params: { department_id?: string; status?: string; q?: string } & PaginationParams,
) {
  return useFetch<PaginatedResponse<Employee>>(
    async () => {
      const data = await apiRequest<BackendEmployee[]>("/employees", {
        params: {
          department: params.department_id,
          status: params.status,
        },
      });
      let employees = data.map(mapEmployee);

      if (params.q) {
        const query = params.q.toLowerCase();
        employees = employees.filter((employee) =>
          `${employee.first_name} ${employee.last_name} ${employee.employee_number} ${employee.email}`
            .toLowerCase()
            .includes(query),
        );
      }

      return paginateItems(employees, params.page, params.page_size);
    },
    [params.department_id, params.status, params.q, params.page, params.page_size],
  );
}

export function useEmployee(id: string | null) {
  return useFetch<Employee | null>(
    async () => {
      if (!id) return null;
      const data = await apiRequest<BackendEmployee>(`/employees/${id}`);
      return mapEmployee(data);
    },
    [id],
  );
}

export function useDepartments() {
  return useFetch<Department[]>(
    async () => {
      const data = await apiRequest<Department[]>("/departments");
      return data.map(mapDepartment);
    },
    [],
  );
}

export function useSchedules() {
  return useFetch<WorkSchedule[]>(
    async () => {
      const data = await apiRequest<WorkSchedule[]>("/work-schedules");
      return data.map((schedule) => ({
        ...schedule,
        id: String(schedule.id),
        total_weekly_hours: Number(schedule.weekly_hours ?? 0),
        days: (schedule.days ?? []).map((day) => ({
          ...day,
          id: day.id == null ? undefined : String(day.id),
        })),
      }));
    },
    [],
  );
}

export function useContracts(params?: { employee_id?: string; status?: string }) {
  return useFetch<Contract[]>(
    async () => {
      const data = await apiRequest<BackendContract[]>("/contracts", {
        params: {
          employee: params?.employee_id,
          status: params?.status,
        },
      });
      return data.map(mapContract);
    },
    [params?.employee_id, params?.status],
  );
}

export function usePaginatedContracts(
  params: { employee_id?: string; status?: string } & PaginationParams,
) {
  return useFetch<PaginatedResponse<Contract>>(
    async () => {
      const data = await apiRequest<BackendContract[]>("/contracts", {
        params: {
          employee: params.employee_id,
          status: params.status,
        },
      });
      return paginateItems(data.map(mapContract), params.page, params.page_size);
    },
    [params.employee_id, params.status, params.page, params.page_size],
  );
}

export const employeeApi = {
  create: (data: Partial<EmployeeFormValues>) => {
    const { department_id, manager_id, work_schedule_id, user_id, ...fields } = data;

    return apiRequest<Employee>("/employees", {
      method: "POST",
      body: {
        ...fields,
        department: department_id || null,
        manager: manager_id || null,
        work_schedule: work_schedule_id || null,
        user: user_id || data.user || null,
      },
    });
  },
  update: (id: string, data: Partial<EmployeeFormValues>) => {
    const { department_id, manager_id, work_schedule_id, user_id, ...fields } = data;

    return apiRequest<Employee>(`/employees/${id}`, {
      method: "PATCH",
      body: {
        ...fields,
        department: department_id || null,
        manager: manager_id || null,
        work_schedule: work_schedule_id || null,
        ...(user_id ? { user: user_id } : {}),
      },
    });
  },
  terminate: (id: string) =>
    apiRequest<Employee>(`/employees/${id}`, { method: "DELETE" }),
};

export const contractApi = {
  create: (data: Partial<Contract>) => {
    const { employee_id, salary_structure_id, work_schedule_id, ...fields } = data;

    return apiRequest<Contract>("/contracts", {
      method: "POST",
      body: {
        ...fields,
        employee: employee_id,
        salary_structure: salary_structure_id,
        work_schedule: work_schedule_id || null,
      },
    });
  },
  update: (id: string, data: Partial<Contract>) => {
    const { employee_id, salary_structure_id, work_schedule_id, ...fields } = data;

    return apiRequest<Contract>(`/contracts/${id}`, {
      method: "PATCH",
      body: {
        ...fields,
        ...(employee_id ? { employee: employee_id } : {}),
        ...(salary_structure_id ? { salary_structure: salary_structure_id } : {}),
        ...(work_schedule_id !== undefined ? { work_schedule: work_schedule_id || null } : {}),
      },
    });
  },
  terminate: (id: string) =>
    apiRequest<Contract>(`/contracts/${id}`, {
      method: "PATCH",
      body: { status: "TERMINATED" },
    }),
};

export const departmentApi = {
  create: (data: Partial<Department>) =>
    apiRequest<Department>("/departments", { method: "POST", body: data }),
  update: (id: string, data: Partial<Department>) =>
    apiRequest<Department>(`/departments/${id}`, { method: "PATCH", body: data }),
};
