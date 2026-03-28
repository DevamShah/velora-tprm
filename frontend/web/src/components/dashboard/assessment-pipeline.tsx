"use client";

import React from "react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const STAGE_CONFIG: Array<{
  key: string;
  label: string;
  color: string;
  bg: string;
}> = [
  { key: "draft", label: "Draft", color: "bg-gray-400", bg: "bg-gray-100" },
  { key: "distributed", label: "Distributed", color: "bg-blue-400", bg: "bg-blue-50" },
  { key: "in_progress", label: "In Progress", color: "bg-indigo-500", bg: "bg-indigo-50" },
  { key: "submitted", label: "Submitted", color: "bg-amber-500", bg: "bg-amber-50" },
  { key: "under_review", label: "Under Review", color: "bg-orange-500", bg: "bg-orange-50" },
  { key: "completed", label: "Completed", color: "bg-green-500", bg: "bg-green-50" },
];

interface AssessmentPipelineProps {
  assessmentsByStatus: Record<string, number>;
  totalAssessments: number;
}

export function AssessmentPipeline({
  assessmentsByStatus,
  totalAssessments,
}: AssessmentPipelineProps) {
  const stages = STAGE_CONFIG.map((stage) => ({
    ...stage,
    count: assessmentsByStatus[stage.key] || 0,
  }));

  const maxCount = Math.max(...stages.map((s) => s.count), 1);

  return (
    <TooltipProvider delayDuration={100}>
      <div className="space-y-3">
        {stages.map((stage) => {
          const percentage =
            totalAssessments > 0
              ? ((stage.count / totalAssessments) * 100).toFixed(0)
              : "0";
          const barWidth =
            maxCount > 0 ? Math.max((stage.count / maxCount) * 100, 2) : 2;

          return (
            <Tooltip key={stage.key}>
              <TooltipTrigger asChild>
                <div className="flex items-center gap-3 group cursor-default">
                  <span className="text-xs text-text-muted font-medium w-24 text-right shrink-0">
                    {stage.label}
                  </span>
                  <div className="flex-1 h-7 rounded-md bg-surface-main/60 overflow-hidden">
                    <div
                      className={cn(
                        "h-full rounded-md transition-all duration-500 flex items-center px-2",
                        stage.color,
                        "group-hover:opacity-90"
                      )}
                      style={{ width: `${barWidth}%` }}
                    >
                      {stage.count > 0 && barWidth > 10 && (
                        <span className="text-xs font-semibold text-white">
                          {stage.count}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-xs font-semibold text-text-primary w-8 text-right">
                    {stage.count}
                  </span>
                </div>
              </TooltipTrigger>
              <TooltipContent side="right" className="text-xs">
                <p className="font-semibold">{stage.label}</p>
                <p className="text-text-muted">
                  {stage.count} assessment{stage.count !== 1 ? "s" : ""} ({percentage}%)
                </p>
              </TooltipContent>
            </Tooltip>
          );
        })}
      </div>
    </TooltipProvider>
  );
}
