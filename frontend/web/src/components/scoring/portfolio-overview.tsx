"use client";

import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ScoreGauge } from "./score-gauge";
import { TierDistribution } from "./tier-distribution";
import { usePortfolioSummary } from "@/hooks/use-scoring";
import { AlertTriangle } from "lucide-react";

interface PortfolioOverviewProps {
  className?: string;
}

export function PortfolioOverview({ className }: PortfolioOverviewProps) {
  const { portfolio, isLoading, error } = usePortfolioSummary();

  if (isLoading) {
    return (
      <Card className={cn(className)}>
        <CardContent className="pt-6 space-y-4">
          <Skeleton className="h-4 w-32" />
          <div className="flex items-center gap-6">
            <Skeleton className="h-24 w-24 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-6 w-full rounded-full" />
              <Skeleton className="h-3 w-3/4" />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !portfolio) {
    return (
      <Card className={cn(className)}>
        <CardContent className="pt-6 flex flex-col items-center justify-center h-40 text-text-muted">
          <AlertTriangle className="h-5 w-5 mb-2 text-risk-medium" />
          <p className="text-sm">{error || "Unable to load portfolio data"}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn(className)}>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-text-primary">
            Portfolio Risk Overview
          </h3>
          <span className="text-xs text-text-muted">
            {portfolio.vendor_count} vendor{portfolio.vendor_count !== 1 ? "s" : ""}
          </span>
        </div>

        <div className="flex items-center gap-6">
          <ScoreGauge score={portfolio.average_score} size="sm" showLabel={false} />
          <div className="flex-1 min-w-0">
            <div className="flex items-baseline gap-2 mb-3">
              <span className="text-2xl font-bold text-text-primary">
                {portfolio.average_score?.toFixed(0) ?? "--"}
              </span>
              <span className="text-xs text-text-muted">avg score</span>
            </div>
            <TierDistribution distribution={portfolio.tier_distribution} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
