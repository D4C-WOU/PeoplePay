const STATUS_STYLES: Record<string, { label: string; fg: string; bg: string }> =
  {
    ACTIVE: {
      label: "Active",
      fg: "var(--pp-success)",
      bg: "var(--pp-success-bg)",
    },
    ON_LEAVE: {
      label: "On leave",
      fg: "var(--pp-warning)",
      bg: "var(--pp-warning-bg)",
    },
    TERMINATED: {
      label: "Terminated",
      fg: "var(--pp-danger)",
      bg: "var(--pp-danger-bg)",
    },
    INACTIVE: { label: "Inactive", fg: "#64748b", bg: "#f1f5f9" },
    PRESENT: {
      label: "Present",
      fg: "var(--pp-success)",
      bg: "var(--pp-success-bg)",
    },
    ABSENT: {
      label: "Absent",
      fg: "var(--pp-danger)",
      bg: "var(--pp-danger-bg)",
    },
    HALF_DAY: {
      label: "Half day",
      fg: "var(--pp-warning)",
      bg: "var(--pp-warning-bg)",
    },
    LATE: {
      label: "Late",
      fg: "var(--pp-warning)",
      bg: "var(--pp-warning-bg)",
    },
    HOLIDAY: {
      label: "Holiday",
      fg: "var(--pp-info)",
      bg: "var(--pp-info-bg)",
    },
    DRAFT: { label: "Draft", fg: "#64748b", bg: "#f1f5f9" },
    PROCESSING: {
      label: "Processing",
      fg: "var(--pp-info)",
      bg: "var(--pp-info-bg)",
    },
    COMPLETED: {
      label: "Finalized",
      fg: "var(--pp-success)",
      bg: "var(--pp-success-bg)",
    },
    CANCELLED: {
      label: "Cancelled",
      fg: "var(--pp-danger)",
      bg: "var(--pp-danger-bg)",
    },
    PENDING: {
      label: "Pending",
      fg: "var(--pp-warning)",
      bg: "var(--pp-warning-bg)",
    },
    APPROVED: {
      label: "Approved",
      fg: "var(--pp-success)",
      bg: "var(--pp-success-bg)",
    },
    REJECTED: {
      label: "Rejected",
      fg: "var(--pp-danger)",
      bg: "var(--pp-danger-bg)",
    },
    FINALIZED: {
      label: "Finalized",
      fg: "var(--pp-success)",
      bg: "var(--pp-success-bg)",
    },
    PAID: {
      label: "Paid",
      fg: "var(--pp-success)",
      bg: "var(--pp-success-bg)",
    },
    EXPIRED: { label: "Expired", fg: "#64748b", bg: "#f1f5f9" },
  };

export function StatusBadge({ status }: { status: string }) {
  const config = STATUS_STYLES[status] ?? {
    label: status.replaceAll("_", " "),
    fg: "#64748b",
    bg: "#f1f5f9",
  };
  return (
    <span className="badge" style={{ color: config.fg, background: config.bg }}>
      <span
        className="size-1.5 rounded-full"
        style={{ background: config.fg }}
      />
      {config.label}
    </span>
  );
}
