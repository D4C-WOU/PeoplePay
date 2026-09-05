"use client";

import { useState } from "react";
import Link from "next/link";
import { FileSignature } from "lucide-react";

import { Header } from "@/components/layout/header";
import { StatusBadge } from "@/components/shared/status-badge";
import { DataTable } from "@/components/shared/data-table";
import { FilterBar } from "@/components/shared/filter-bar";
import { ContractDialog } from "@/components/contracts/contract-dialog";
import { useEmployees, usePaginatedContracts } from "@/hooks/useEmployees";

const PAGE_SIZE = 10;

function money(value: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

export default function ContractsPage() {
  const [page, setPage] = useState(1);
  const {
    data: contractPage,
    loading,
    error,
    reload,
  } = usePaginatedContracts({ page, page_size: PAGE_SIZE });
  const { data: employees } = useEmployees();
  const contracts = contractPage?.items ?? [];

  const employeeName = (id: string) => {
    const emp = employees?.find((e) => e.id === id);
    return emp ? `${emp.first_name} ${emp.last_name}` : id;
  };

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title="Contracts"
        description="Every employment term, historized — payroll only ever uses the one active for its period."
        actions={
          <ContractDialog
            onCreated={() => {
              setPage(1);
              reload();
            }}
          />
        }
      />

      <div className="flex-1 space-y-4 p-4 sm:p-6">
        <FilterBar />
        <DataTable
          rows={contracts}
          rowKey={(contract) => contract.id}
          loading={loading}
          error={error}
          emptyIcon={FileSignature}
          emptyTitle="No contracts yet"
          emptyDescription="Create the first employment contract for an employee."
          page={contractPage?.page}
          pageSize={contractPage?.page_size}
          total={contractPage?.total}
          pages={contractPage?.pages}
          onPageChange={setPage}
          columns={[
            {
              key: "number",
              header: "Contract #",
              render: (contract) => (
                <Link
                  href={`/dashboard/contracts/${contract.id}`}
                  className="font-medium"
                >
                  {contract.contract_number}
                </Link>
              ),
            },
            {
              key: "employee",
              header: "Employee",
              render: (contract) => employeeName(contract.employee_id),
            },
            {
              key: "start",
              header: "Start",
              render: (contract) => contract.start_date,
            },
            {
              key: "end",
              header: "End",
              render: (contract) => contract.end_date ?? "Open-ended",
            },
            {
              key: "type",
              header: "Type",
              className: "capitalize text-muted-foreground",
              render: (contract) =>
                contract.contract_type.replaceAll("_", " ").toLowerCase(),
            },
            {
              key: "salary",
              header: "Base salary",
              render: (contract) =>
                money(contract.base_salary, contract.currency),
            },
            {
              key: "status",
              header: "Status",
              render: (contract) => <StatusBadge status={contract.status} />,
            },
          ]}
        />
      </div>
    </div>
  );
}
