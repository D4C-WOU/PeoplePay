"use client";

import { useState } from "react";
import Link from "next/link";
import { FileSignature } from "lucide-react";

import { Header } from "@/components/layout/header";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StatusBadge } from "@/components/shared/status-badge";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { EmptyState } from "@/components/shared/empty-state";
import { Pagination } from "@/components/shared/pagination";
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
        actions={<ContractDialog onCreated={() => { setPage(1); reload(); }} />}
      />

      <div className="flex-1 space-y-4 p-4 sm:p-6">
        {error && <ErrorBanner message={error} />}
        {loading ? (
          <LoadingBanner label="Loading contracts…" />
        ) : contracts.length === 0 ? (
          <EmptyState
            icon={FileSignature}
            title="No contracts yet"
            description="Create the first employment contract for an employee."
          />
        ) : (
          <div className="overflow-hidden rounded-xl border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Contract #</TableHead>
                  <TableHead>Employee</TableHead>
                  <TableHead>Start</TableHead>
                  <TableHead>End</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Base salary</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {contracts.map((c) => (
                  <TableRow key={c.id}>
                    <TableCell className="font-medium">
                      <Link href={`/dashboard/contracts/${c.id}`}>
                        {c.contract_number}
                      </Link>
                    </TableCell>
                    <TableCell>{employeeName(c.employee_id)}</TableCell>
                    <TableCell>{c.start_date}</TableCell>
                    <TableCell>{c.end_date ?? "Open-ended"}</TableCell>
                    <TableCell className="capitalize text-muted-foreground">
                      {c.contract_type.replaceAll("_", " ").toLowerCase()}
                    </TableCell>
                    <TableCell>{money(c.base_salary, c.currency)}</TableCell>
                    <TableCell>
                      <StatusBadge status={c.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {contractPage && (
              <Pagination
                page={contractPage.page}
                pageSize={contractPage.page_size}
                total={contractPage.total}
                pages={contractPage.pages}
                onPageChange={setPage}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
