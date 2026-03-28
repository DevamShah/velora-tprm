"use client";

import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { ScoreGauge } from "./score-gauge";
import { TierDistribution } from "./tier-distribution";
import type { PortfolioSummary as PortfolioSummaryType } from "@/types/scoring";
import { getTierColor } from "@/types/scoring";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from "recharts";

interface PortfolioSummaryProps {
  portfolio: PortfolioSummaryType;
  className?: string;
}

const RISK_LABELS: Record<string, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  minimal: "Minimal",
};

export function PortfolioSummaryView({ portfolio, className }: PortfolioSummaryProps) {
  const riskData = Object.entries(portfolio.risk_distribution)
    .filter(([, v]) => v > 0)
    .map(([key, value]) => ({
      name: RISK_LABELS[key] || key,
      value,
      color: getTierColor(key as "critical" | "high" | "medium" | "low" | "minimal"),
    }));

  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4", className)}>
      {/* Average Score */}
      <Card>
        <CardContent className="pt-6 flex flex-col items-center">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">
            Portfolio Score
          </p>
          <ScoreGauge score={portfolio.average_score} size="md" />
        </CardContent>
      </Card>

      {/* Vendor Count */}
      <Card>
        <CardContent className="pt-6 flex flex-col items-center justify-center">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">
            Total Vendors
          </p>
          <span className="text-4xl font-bold text-text-primary">
            {portfolio.vendor_count}
          </span>
          <span className="text-xs text-text-muted mt-1">
            scored vendors
          </span>
        </CardContent>
      </Card>

      {/* Tier Distribution */}
      <Card>
        <CardContent className="pt-6">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">
            Tier Distribution
          </p>
          <TierDistribution distribution={portfolio.tier_distribution} />
        </CardContent>
      </Card>

      {/* Risk Distribution Pie */}
      <Card>
        <CardContent className="pt-6">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
            Risk Distribution
          </p>
          {riskData.length === 0 ? (
            <div className="flex items-center justify-center h-32 text-text-muted text-sm">
              No risk data
            </div>
          ) : (
            <div className="h-36">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    innerRadius={28}
                    outerRadius={52}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {riskData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip
                    content={<RiskTooltip />}
                    wrapperStyle={{ outline: "none" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function RiskTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: { name: string; value: number; color: string } }> }) {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0].payload;

  return (
    <div className="rounded-lg border border-surface-card-border bg-white px-3 py-2 shadow-md">
      <div className="flex items-center gap-2">
        <span
          className="w-2.5 h-2.5 rounded-full"
          style={{ backgroundColor: data.color }}
        />
        <span className="text-xs font-medium text-text-primary">
          {data.name}: {data.value}
        </span>
      </div>
    </div>
  );
}
