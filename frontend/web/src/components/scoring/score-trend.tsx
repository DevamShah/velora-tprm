"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { cn } from "@/lib/utils";
import type { ScoreHistoryItem } from "@/types/scoring";
import { getScoreColor } from "@/types/scoring";

interface ScoreTrendProps {
  history: ScoreHistoryItem[];
  className?: string;
}

export function ScoreTrend({ history, className }: ScoreTrendProps) {
  if (!history || history.length === 0) {
    return (
      <div className={cn("flex items-center justify-center h-48 text-text-muted text-sm", className)}>
        No score history available
      </div>
    );
  }

  const data = [...history]
    .sort(
      (a, b) =>
        new Date(a.calculated_at).getTime() -
        new Date(b.calculated_at).getTime()
    )
    .map((item) => ({
      date: formatShortDate(item.calculated_at),
      score: item.overall_score,
      tier: item.tier,
    }));

  const latestScore = data[data.length - 1]?.score ?? 50;
  const lineColor = getScoreColor(latestScore);

  return (
    <div className={cn("w-full h-48", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: -8 }}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--color-surface-card-border, #e2e8f0)"
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "var(--color-text-muted, #64748b)" }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: "var(--color-text-muted, #94a3b8)" }}
            tickLine={false}
            axisLine={false}
            tickCount={5}
          />
          <Tooltip
            content={<TrendTooltip />}
            wrapperStyle={{ outline: "none" }}
          />
          <Line
            type="monotone"
            dataKey="score"
            stroke={lineColor}
            strokeWidth={2}
            dot={{ fill: lineColor, r: 3, strokeWidth: 0 }}
            activeDot={{ fill: lineColor, r: 5, strokeWidth: 2, stroke: "#fff" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function TrendTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: { date: string; score: number; tier: string } }> }) {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0].payload;

  return (
    <div className="rounded-lg border border-surface-card-border bg-surface-card px-3 py-2 shadow-md">
      <p className="text-xs font-medium text-text-muted mb-0.5">{data.date}</p>
      <p className="text-sm font-semibold" style={{ color: getScoreColor(data.score) }}>
        Score: {data.score}
      </p>
      <p className="text-xs text-text-secondary capitalize">Tier: {data.tier}</p>
    </div>
  );
}

function formatShortDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}
