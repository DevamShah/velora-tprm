import React from "react";
import { cn } from "@/lib/utils";
import type { AlertPriority } from "@/types/monitoring";

const PRIORITY_STYLES: Record<AlertPriority, string> = {
  p0: "bg-red-100 text-red-700 border-red-200",
  p1: "bg-orange-100 text-orange-700 border-orange-200",
  p2: "bg-yellow-100 text-yellow-700 border-yellow-200",
  p3: "bg-blue-100 text-blue-700 border-blue-200",
  p4: "bg-gray-100 text-gray-600 border-gray-200",
};

const PRIORITY_DOT: Record<AlertPriority, string> = {
  p0: "bg-red-500",
  p1: "bg-orange-500",
  p2: "bg-yellow-500",
  p3: "bg-blue-500",
  p4: "bg-gray-400",
};

const PRIORITY_LABELS: Record<AlertPriority, string> = {
  p0: "P0 Critical",
  p1: "P1 High",
  p2: "P2 Medium",
  p3: "P3 Low",
  p4: "P4 Info",
};

interface AlertPriorityBadgeProps {
  priority: AlertPriority;
  className?: string;
  size?: "sm" | "md";
}

export function AlertPriorityBadge({
  priority,
  className,
  size = "sm",
}: AlertPriorityBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-medium",
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm",
        PRIORITY_STYLES[priority],
        className
      )}
    >
      <span
        className={cn(
          "rounded-full shrink-0",
          size === "sm" ? "w-1.5 h-1.5" : "w-2 h-2",
          PRIORITY_DOT[priority]
        )}
      />
      {PRIORITY_LABELS[priority]}
    </span>
  );
}
