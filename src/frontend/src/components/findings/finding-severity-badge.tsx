import React from "react";
import { cn } from "@/lib/utils";
import type { FindingSeverity } from "@/types/finding";

const SEVERITY_STYLES: Record<FindingSeverity, string> = {
  critical: "bg-red-100 text-red-700 border-red-200",
  high: "bg-orange-100 text-orange-700 border-orange-200",
  medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  low: "bg-green-100 text-green-700 border-green-200",
  info: "bg-gray-100 text-gray-600 border-gray-200",
};

const SEVERITY_DOT: Record<FindingSeverity, string> = {
  critical: "bg-red-500",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
  low: "bg-green-500",
  info: "bg-gray-400",
};

const SEVERITY_LABELS: Record<FindingSeverity, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  info: "Info",
};

interface FindingSeverityBadgeProps {
  severity: FindingSeverity;
  className?: string;
  size?: "sm" | "md";
}

export function FindingSeverityBadge({
  severity,
  className,
  size = "sm",
}: FindingSeverityBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-medium",
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm",
        SEVERITY_STYLES[severity],
        className
      )}
    >
      <span
        className={cn(
          "rounded-full shrink-0",
          size === "sm" ? "w-1.5 h-1.5" : "w-2 h-2",
          SEVERITY_DOT[severity]
        )}
      />
      {SEVERITY_LABELS[severity]}
    </span>
  );
}
