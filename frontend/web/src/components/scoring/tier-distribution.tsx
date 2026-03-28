"use client";

import { cn } from "@/lib/utils";
import { getTierColor } from "@/types/scoring";

interface TierDistributionProps {
  distribution: Record<string, number>;
  className?: string;
}

const TIER_ORDER = ["critical", "high", "medium", "low", "minimal"];

export function TierDistribution({ distribution, className }: TierDistributionProps) {
  const total = Object.values(distribution).reduce((s, v) => s + v, 0);

  if (total === 0) {
    return (
      <div className={cn("flex items-center justify-center h-16 text-text-muted text-sm", className)}>
        No tier data
      </div>
    );
  }

  const tiers = TIER_ORDER.filter((t) => (distribution[t] ?? 0) > 0);

  return (
    <div className={cn("space-y-3", className)}>
      {/* Stacked bar */}
      <div className="flex h-6 rounded-full overflow-hidden bg-surface-main">
        {tiers.map((tier) => {
          const count = distribution[tier] ?? 0;
          const percent = (count / total) * 100;
          return (
            <div
              key={tier}
              className="h-full transition-all duration-500 first:rounded-l-full last:rounded-r-full"
              style={{
                width: `${percent}%`,
                backgroundColor: getTierColor(tier as "critical" | "high" | "medium" | "low" | "minimal"),
                minWidth: count > 0 ? "8px" : undefined,
              }}
            />
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-1.5">
        {TIER_ORDER.map((tier) => {
          const count = distribution[tier] ?? 0;
          if (count === 0) return null;
          const percent = ((count / total) * 100).toFixed(0);
          return (
            <div key={tier} className="flex items-center gap-1.5">
              <span
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ backgroundColor: getTierColor(tier as "critical" | "high" | "medium" | "low" | "minimal") }}
              />
              <span className="text-xs text-text-secondary capitalize">
                {tier}
              </span>
              <span className="text-xs font-medium text-text-primary">
                {count} ({percent}%)
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
