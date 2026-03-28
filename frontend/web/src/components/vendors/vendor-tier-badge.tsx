import { Badge } from "@/components/ui/badge";
import type { VendorTier } from "@/types/vendor";

const TIER_VARIANT: Record<VendorTier, "critical" | "high" | "medium" | "low" | "secondary"> = {
  critical: "critical",
  high: "high",
  medium: "medium",
  low: "low",
  unclassified: "secondary",
};

const TIER_LABEL: Record<VendorTier, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  unclassified: "Unclassified",
};

interface VendorTierBadgeProps {
  tier: VendorTier;
  className?: string;
}

export function VendorTierBadge({ tier, className }: VendorTierBadgeProps) {
  return (
    <Badge variant={TIER_VARIANT[tier]} className={className}>
      {TIER_LABEL[tier]}
    </Badge>
  );
}
