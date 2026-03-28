import { Badge } from "@/components/ui/badge";
import type { AlertStatus } from "@/types/monitoring";
import { ALERT_STATUS_LABELS } from "@/types/monitoring";

const STATUS_VARIANT: Record<AlertStatus, "default" | "secondary" | "outline" | "low" | "critical" | "high" | "medium"> = {
  new: "critical",
  acknowledged: "high",
  investigating: "default",
  resolved: "low",
  suppressed: "secondary",
};

interface AlertStatusBadgeProps {
  status: AlertStatus;
  className?: string;
}

export function AlertStatusBadge({ status, className }: AlertStatusBadgeProps) {
  return (
    <Badge variant={STATUS_VARIANT[status]} className={className}>
      {ALERT_STATUS_LABELS[status]}
    </Badge>
  );
}
