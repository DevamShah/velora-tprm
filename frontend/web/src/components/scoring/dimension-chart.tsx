"use client";

import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
} from "recharts";
import { cn } from "@/lib/utils";
import type { DimensionScore } from "@/types/scoring";

interface DimensionChartProps {
  dimensions: DimensionScore[];
  className?: string;
}

export function DimensionChart({ dimensions, className }: DimensionChartProps) {
  if (!dimensions || dimensions.length === 0) {
    return (
      <div className={cn("flex items-center justify-center h-64 text-text-muted text-sm", className)}>
        No dimension data available
      </div>
    );
  }

  const data = dimensions.map((d) => ({
    dimension: formatDimensionLabel(d.dimension),
    score: d.score,
    weight: d.weight,
    weighted: d.weighted_score,
    fullMark: 100,
  }));

  return (
    <div className={cn("w-full h-64", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid
            stroke="var(--color-surface-card-border, #e2e8f0)"
            strokeDasharray="3 3"
          />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fontSize: 11, fill: "var(--color-text-muted, #64748b)" }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fontSize: 10, fill: "var(--color-text-muted, #94a3b8)" }}
            tickCount={5}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.2}
            strokeWidth={2}
          />
          <Tooltip
            content={<DimensionTooltip />}
            wrapperStyle={{ outline: "none" }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

function DimensionTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: { dimension: string; score: number; weight: number; weighted: number } }> }) {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0].payload;

  return (
    <div className="rounded-lg border border-surface-card-border bg-white px-3 py-2 shadow-md">
      <p className="text-xs font-semibold text-text-primary mb-1">
        {data.dimension}
      </p>
      <div className="space-y-0.5 text-xs text-text-secondary">
        <p>Score: <span className="font-medium text-text-primary">{data.score}</span></p>
        <p>Weight: <span className="font-medium text-text-primary">{(data.weight * 100).toFixed(0)}%</span></p>
        <p>Weighted: <span className="font-medium text-text-primary">{data.weighted.toFixed(1)}</span></p>
      </div>
    </div>
  );
}

function formatDimensionLabel(s: string): string {
  return s
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
