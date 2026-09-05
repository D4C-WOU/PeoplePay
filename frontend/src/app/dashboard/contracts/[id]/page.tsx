"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { Ban, Loader2 } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/shared/status-badge";
import { LoadingBanner, ErrorBanner } from "@/components/shared/state-banner";
import { useFetch } from "@/hooks/useFetch";
import { apiRequest, ApiError } from "@/lib/api";
import { contractApi, useEmployees } from "@/hooks/useEmployees";
import type { Contract } from "@/types/employee";

function money(value: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value ?? 0);
}

export default function ContractDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const {
    data: contract,
    loading,
    error,
    reload,
  } = useFetch<Contract>(
    () => apiRequest<Contract>(`/contracts/${params.id}`),
    [params.id],
  );
  const { data: employees } = useEmployees();
  const [actionError, setActionError] = useState<string | null>(null);
  const [terminating, setTerminating] = useState(false);

  const employee = employees?.find((e) => e.id === contract?.employee_id);

  async function handleTerminate() {
    if (!contract) return;
    setTerminating(true);
    setActionError(null);
    try {
      await contractApi.terminate(contract.id);
      reload();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : "Could not terminate contract.",
      );
    } finally {
      setTerminating(false);
    }
  }

  if (loading) return <LoadingBanner label="Loading contract…" />;
  if (error) return <ErrorBanner message={error} />;
  if (!contract) return null;

  return (
    <div className="flex flex-1 flex-col">
      <Header
        title={contract.contract_number}
        description={
          employee
            ? `${employee.first_name} ${employee.last_name}`
            : contract.employee_id
        }
        actions={
          contract.status === "ACTIVE" && (
            <Button
              variant="destructive"
              onClick={handleTerminate}
              disabled={terminating}
            >
              {terminating ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Ban />
              )}
              Terminate contract
            </Button>
          )
        }
      />
      <div className="flex-1 space-y-4 p-4 sm:p-6">
        {actionError && <ErrorBanner message={actionError} />}
        <Card>
          <CardContent className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <Info
              label="Status"
              value={<StatusBadge status={contract.status} />}
            />
            <Info label="Start date" value={contract.start_date} />
            <Info label="End date" value={contract.end_date ?? "Open-ended"} />
            <Info
              label="Contract type"
              value={contract.contract_type.replaceAll("_", " ")}
            />
            <Info
              label="Base salary"
              value={money(contract.base_salary, contract.currency)}
            />
            <Info label="Currency" value={contract.currency} />
          </CardContent>
        </Card>
        {contract.notes && (
          <Card>
            <CardContent>
              <p className="text-sm text-muted-foreground">{contract.notes}</p>
            </CardContent>
          </Card>
        )}
        <Button
          variant="outline"
          onClick={() => router.push("/dashboard/contracts")}
        >
          Back to contracts
        </Button>
      </div>
    </div>
  );
}

function Info({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-medium capitalize">{value}</p>
    </div>
  );
}
