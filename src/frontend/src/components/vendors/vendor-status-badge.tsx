import { Badge } from "@/components/ui/badge";
import type { VendorStatus } from "@/types/vendor";

const STATUS_VARIANT: Record<VendorStatus, "default" | "secondary" | "outline" | "low" | "high" | "critical"> = {
  discovered: "outline",
  classified: "secondary",
  assessing: "default",
  active: "low",
  monitoring: "default",
  reassessing: "high",
  offboarding: "high",
  offboarded: "secondary",
  archived: "outline",
};

const STATUS_LABEL: Record<VendorStatus, string> = {
  discovered: "Discovered",
  classified: "Classified",
  assessing: "Assessing",
  active: "Active",
  monitoring: "Monitoring",
  reassessing: "Reassessing",
  offboarding: "Offboarding",
  offboarded: "Offboarded",
  archived: "Archived",
};

interface VendorStatusBadgeProps {
  status: VendorStatus;
  className?: string;
}

export function VendorStatusBadge({ status, className }: VendorStatusBadgeProps) {
  return (
    <Badge variant={STATUS_VARIANT[status]} className={className}>
      {STATUS_LABEL[status]}
    </Badge>
  );
}
