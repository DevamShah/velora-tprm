"use client";

import React from "react";
import Link from "next/link";
import { TrendingUp, TrendingDown, Minus, Building2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { DashboardVendor } from "@/types/dashboard";

const TIER_VARIANT: Record<string, "critical" | "high" | "medium" | "low" | "secondary"> = {
  critical: "critical",
  high: "high",
  medium: "medium",
  low: "low",
  unclassified: "secondary",
};

function getRiskColor(score: number): string {
  if (score >= 80) return "text-risk-critical";
  if (score >= 60) return "text-risk-high";
  if (score >= 40) return "text-amber-600";
  if (score >= 20) return "text-risk-low";
  return "text-risk-minimal";
}

function getRiskBg(score: number): string {
  if (score >= 80) return "bg-risk-critical/10";
  if (score >= 60) return "bg-risk-high/10";
  if (score >= 40) return "bg-amber-100";
  if (score >= 20) return "bg-risk-low/10";
  return "bg-risk-minimal/10";
}

interface TopRiskVendorsProps {
  vendors: DashboardVendor[];
}

export function TopRiskVendors({ vendors }: TopRiskVendorsProps) {
  if (vendors.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-surface-main mb-3">
          <Building2 className="w-5 h-5 text-text-muted" />
        </div>
        <p className="text-sm text-text-muted">No vendor risk data</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-surface-card-border">
            <th className="text-left py-2 text-xs font-semibold text-text-muted uppercase tracking-wider">
              Vendor
            </th>
            <th className="text-center py-2 text-xs font-semibold text-text-muted uppercase tracking-wider w-20">
              Tier
            </th>
            <th className="text-right py-2 text-xs font-semibold text-text-muted uppercase tracking-wider w-20">
              Score
            </th>
            <th className="text-center py-2 text-xs font-semibold text-text-muted uppercase tracking-wider w-16">
              Trend
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-card-border">
          {vendors.map((vendor, idx) => (
            <tr key={vendor.id} className="group">
              <td className="py-2.5">
                <Link
                  href={`/vendors/${vendor.id}`}
                  className="flex items-center gap-2 hover:text-accent-primary transition-colors"
                >
                  <span className="text-xs text-text-muted font-medium w-5">
                    {idx + 1}.
                  </span>
                  <span className="font-medium text-text-primary group-hover:text-accent-primary transition-colors truncate">
                    {vendor.name}
                  </span>
                </Link>
              </td>
              <td className="py-2.5 text-center">
                <Badge
                  variant={TIER_VARIANT[vendor.tier] || "secondary"}
                  className="text-[10px]"
                >
                  {vendor.tier}
                </Badge>
              </td>
              <td className="py-2.5 text-right">
                <span
                  className={cn(
                    "inline-flex items-center justify-center rounded-md px-2 py-0.5 text-xs font-semibold",
                    getRiskColor(vendor.risk_score),
                    getRiskBg(vendor.risk_score)
                  )}
                >
                  {vendor.risk_score}
                </span>
              </td>
              <td className="py-2.5">
                <div className="flex justify-center">
                  {vendor.trend === "up" && (
                    <TrendingUp className="w-4 h-4 text-risk-critical" />
                  )}
                  {vendor.trend === "down" && (
                    <TrendingDown className="w-4 h-4 text-risk-low" />
                  )}
                  {vendor.trend === "stable" && (
                    <Minus className="w-4 h-4 text-text-muted" />
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
