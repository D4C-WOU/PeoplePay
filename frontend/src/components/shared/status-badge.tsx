import { Badge } from "@/components/ui/badge";

const STATUS_STYLES: Record<
  string,
  { label: string; variant: "default" | "secondary" | "destructive" | "outline" }
> = {
  ACTIVE: { label: "Active", variant: "default" },
  ON_LEAVE: { label: "On leave", variant: "secondary" },
  TERMINATED: { label: "Terminated", variant: "destructive" },
  PRESENT: { label: "Present", variant: "default" },
  ABSENT: { label: "Absent", variant: "destructive" },
  HALF_DAY: { label: "Half day", variant: "secondary" },
  LATE: { label: "Late", variant: "secondary" },
  HOLIDAY: { label: "Holiday", variant: "outline" },
  DRAFT: { label: "Draft", variant: "outline" },
  PROCESSING: { label: "Processing", variant: "secondary" },
  COMPLETED: { label: "Completed", variant: "default" },
  CANCELLED: { label: "Cancelled", variant: "destructive" },
  PENDING: { label: "Pending", variant: "secondary" },
  APPROVED: { label: "Approved", variant: "default" },
  REJECTED: { label: "Rejected", variant: "destructive" },
  FINALIZED: { label: "Finalized", variant: "default" },
  PAID: { label: "Paid", variant: "default" },
  EXPIRED: { label: "Expired", variant: "secondary" },
};

export function StatusBadge({ status }: { status: string }) {
  const config = STATUS_STYLES[status] ?? {
    label: status,
    variant: "outline" as const,
  };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
