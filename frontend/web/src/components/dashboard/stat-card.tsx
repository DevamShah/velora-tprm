"use client";

import React from "react";
import { type LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: "up" | "down" | "stable";
  trendValue?: string;
  breakdown?: Record<string, number>;
  breakdownColors?: Record<string, string>;
  className?: string;
}

export function StatCard({
  label,
  value,
  icon: Icon,
  trend,
  trendValue,
  breakdown,
  breakdownColors,
  className,
}: StatCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-surface-card-border bg-surface-card p-5 velora-card-hover",
        className
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-accent-primary/10">
          <Icon className="w-4.5 h-4.5 text-accent-primary" />
        </div>
        {trend && (
          <div
            className={cn(
              "flex items-center gap-0.5 text-xs font-medium rounded-full px-2 py-0.5",
              trend === "up" && "text-risk-critical bg-risk-critical/10",
              trend === "down" && "text-risk-low bg-risk-low/10",
              trend === "stable" && "text-text-muted bg-surface-main"
            )}
          >
            {trend === "up" && <TrendingUp className="w-3 h-3" />}
            {trend === "down" && <TrendingDown className="w-3 h-3" />}
            {trend === "stable" && <Minus className="w-3 h-3" />}
            {trendValue}
          </div>
        )}
      </div>
      <p className="text-2xl font-semibold text-text-primary tracking-tight">
        {value}
      </p>
      <p className="text-sm text-text-muted mt-0.5">{label}</p>
      {breakdown && Object.keys(breakdown).length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-surface-card-border">
          {Object.entries(breakdown).map(([key, count]) => (
            <span
              key={key}
              className={cn(
                "inline-flex items-center gap-1 text-xs font-medium",
                breakdownColors?.[key] || "text-text-muted"
              )}
            >
              <span
                className={cn(
                  "w-1.5 h-1.5 rounded-full",
                  breakdownColors?.[key]
                    ? breakdownColors[key].replace("text-", "bg-")
                    : "bg-text-muted"
                )}
              />
              {key}: {count}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
