"use client";

import React from "react";
import { Building2, ClipboardCheck, AlertTriangle, Bell, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/dashboard/stat-card";
import { RiskHeatmap } from "@/components/dashboard/risk-heatmap";
import { VendorRiskDonut } from "@/components/dashboard/vendor-risk-donut";
import { RiskTrendChart } from "@/components/dashboard/risk-trend-chart";
import { AssessmentPipeline } from "@/components/dashboard/assessment-pipeline";
import { RecentAlerts } from "@/components/dashboard/recent-alerts";
import { TopRiskVendors } from "@/components/dashboard/top-risk-vendors";
import { useDashboard } from "@/hooks/use-dashboard";

const TIER_COLORS: Record<string, string> = {
  critical: "text-risk-critical",
  high: "text-risk-high",
  medium: "text-amber-600",
  low: "text-risk-low",
  unclassified: "text-text-muted",
};

const SEVERITY_COLORS: Record<string, string> = {
  critical: "text-risk-critical",
  high: "text-risk-high",
  medium: "text-amber-600",
  low: "text-risk-low",
  info: "text-text-muted",
};

const PRIORITY_COLORS: Record<string, string> = {
  p0: "text-red-600",
  p1: "text-orange-600",
  p2: "text-yellow-600",
  p3: "text-blue-600",
  p4: "text-gray-500",
};

export default function DashboardPage() {
  const { data, isLoading, error, refetch } = useDashboard();

  if (error) {
    toast.error(error);
  }

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (!data) {
    return (
      <>
        <PageHeader
          title="Dashboard"
          description="Overview of your third-party risk posture"
        />
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <AlertTriangle className="w-8 h-8 text-text-muted mb-3" />
          <p className="text-sm text-text-muted">
            Unable to load dashboard data. Please try again.
          </p>
          <Button variant="outline" size="sm" className="mt-4" onClick={refetch}>
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            Retry
          </Button>
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Overview of your third-party risk posture"
        actions={
          <Button variant="outline" size="sm" onClick={refetch}>
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            Refresh
          </Button>
        }
      />

      {/* Stat Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        <StatCard
          label="Total Vendors"
          value={data.total_vendors}
          icon={Building2}
          breakdown={data.vendors_by_tier}
          breakdownColors={TIER_COLORS}
        />
        <StatCard
          label="Active Assessments"
          value={data.total_assessments}
          icon={ClipboardCheck}
          breakdown={data.assessments_by_status}
        />
        <StatCard
          label="Open Findings"
          value={data.open_findings}
          icon={AlertTriangle}
          breakdown={data.findings_by_severity}
          breakdownColors={SEVERITY_COLORS}
        />
        <StatCard
          label="Active Alerts"
          value={data.active_alerts}
          icon={Bell}
          breakdown={data.alerts_by_priority}
          breakdownColors={PRIORITY_COLORS}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid gap-4 lg:grid-cols-2 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Risk Heatmap</CardTitle>
          </CardHeader>
          <CardContent>
            <RiskHeatmap vendorsByRisk={data.vendors_by_tier} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Vendor Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <VendorRiskDonut
              vendorsByTier={data.vendors_by_tier}
              totalVendors={data.total_vendors}
            />
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid gap-4 lg:grid-cols-2 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Risk Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <RiskTrendChart avgRiskScore={data.avg_risk_score} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Assessment Pipeline</CardTitle>
          </CardHeader>
          <CardContent>
            <AssessmentPipeline
              assessmentsByStatus={data.assessments_by_status}
              totalAssessments={data.total_assessments}
            />
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Top Risk Vendors</CardTitle>
              <span className="text-xs text-text-muted">Top 10</span>
            </div>
          </CardHeader>
          <CardContent>
            <TopRiskVendors vendors={data.top_risk_vendors} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Recent Alerts</CardTitle>
              <span className="text-xs text-text-muted">
                {data.recent_alerts.length} latest
              </span>
            </div>
          </CardHeader>
          <CardContent>
            <RecentAlerts alerts={data.recent_alerts} />
          </CardContent>
        </Card>
      </div>
    </>
  );
}

function DashboardSkeleton() {
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-40" />
          <Skeleton className="h-4 w-64" />
        </div>
        <Skeleton className="h-9 w-24" />
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-32 rounded-xl" />
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Skeleton className="h-72 rounded-xl" />
        <Skeleton className="h-72 rounded-xl" />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Skeleton className="h-64 rounded-xl" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Skeleton className="h-80 rounded-xl" />
        <Skeleton className="h-80 rounded-xl" />
      </div>
    </div>
  );
}
