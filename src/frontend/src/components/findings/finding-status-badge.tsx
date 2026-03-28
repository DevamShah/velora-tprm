import React from "react";
import { cn } from "@/lib/utils";
import type { FindingStatus } from "@/types/finding";

const STATUS_STYLES: Record<FindingStatus, string> = {
  open: "bg-red-50 text-red-700",
  in_progress: "bg-blue-50 text-blue-700",
  remediated: "bg-green-50 text-green-700",
  accepted: "bg-purple-50 text-purple-700",
  closed: "bg-gray-100 text-gray-600",
  false_positive: "bg-gray-100 text-gray-500",
};

const STATUS_LABELS: Record<FindingStatus, string> = {
  open: "Open",
  in_progress: "In Progress",
  remediated: "Remediated",
  accepted: "Accepted",
  closed: "Closed",
  false_positive: "False Positive",
};

interface FindingStatusBadgeProps {
  status: FindingStatus;
  className?: string;
}

export function FindingStatusBadge({
  status,
  className,
}: FindingStatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        STATUS_STYLES[status],
        className
      )}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}
