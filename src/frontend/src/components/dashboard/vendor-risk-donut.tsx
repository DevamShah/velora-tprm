"use client";

import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

const TIER_COLORS: Record<string, string> = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#eab308",
  low: "#22c55e",
  unclassified: "#94a3b8",
};

const TIER_LABELS: Record<string, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  unclassified: "Unclassified",
};

interface VendorRiskDonutProps {
  vendorsByTier: Record<string, number>;
  totalVendors: number;
}

export function VendorRiskDonut({
  vendorsByTier,
  totalVendors,
}: VendorRiskDonutProps) {
  const data = Object.entries(vendorsByTier)
    .filter(([, count]) => count > 0)
    .map(([tier, count]) => ({
      name: TIER_LABELS[tier] || tier,
      value: count,
      color: TIER_COLORS[tier] || "#94a3b8",
    }));

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-text-muted">
        No vendor data available
      </div>
    );
  }

  return (
    <div className="flex items-center gap-6">
      <div className="relative w-48 h-48">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={3}
              dataKey="value"
              strokeWidth={0}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const item = payload[0];
                return (
                  <div className="rounded-lg border border-surface-card-border bg-white px-3 py-2 shadow-sm text-xs">
                    <p className="font-semibold text-text-primary">
                      {item.name}
                    </p>
                    <p className="text-text-muted">
                      {item.value} vendor{Number(item.value) !== 1 ? "s" : ""} (
                      {((Number(item.value) / totalVendors) * 100).toFixed(0)}%)
                    </p>
                  </div>
                );
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-semibold text-text-primary">
            {totalVendors}
          </span>
          <span className="text-xs text-text-muted">Total</span>
        </div>
      </div>
      <div className="flex flex-col gap-2">
        {data.map((entry) => (
          <div key={entry.name} className="flex items-center gap-2">
            <span
              className="w-2.5 h-2.5 rounded-full shrink-0"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm text-text-secondary">
              {entry.name}
            </span>
            <span className="text-sm font-semibold text-text-primary ml-auto">
              {entry.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
