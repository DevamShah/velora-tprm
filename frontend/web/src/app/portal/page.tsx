"use client";

import { useEffect, useState } from "react";

interface PortalDashboard {
  pending_assessments: number;
  open_findings: number;
  evidence_requests: number;
  upcoming_deadlines: string[];
}

export default function PortalDashboardPage() {
  const [data, setData] = useState<PortalDashboard | null>(null);

  useEffect(() => {
    fetch("/api/portal/dashboard")
      .then((r) => r.json())
      .then(setData)
      .catch(() => {});
  }, []);

  return (
    <div className="animate-fade-in space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">
          Vendor Dashboard
        </h1>
        <p className="mt-1 text-sm text-text-secondary">
          View your pending assessments, findings, and deadlines.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          title="Pending Assessments"
          value={data?.pending_assessments ?? 0}
          color="accent-primary"
        />
        <StatCard
          title="Open Findings"
          value={data?.open_findings ?? 0}
          color="risk-high"
        />
        <StatCard
          title="Evidence Requests"
          value={data?.evidence_requests ?? 0}
          color="risk-medium"
        />
      </div>

      {/* Action Items */}
      <div className="rounded-xl border border-border-default bg-white p-6 shadow-sm">
        <h2 className="text-lg font-medium text-text-primary">
          Action Items
        </h2>
        <p className="mt-4 text-sm text-text-secondary">
          No pending action items. You&apos;re all caught up.
        </p>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  color,
}: {
  title: string;
  value: number;
  color: string;
}) {
  return (
    <div className="rounded-xl border border-border-default bg-white p-5 shadow-sm transition-all hover:shadow-md">
      <p className="text-sm font-medium text-text-secondary">{title}</p>
      <p className={`mt-2 text-3xl font-bold text-${color}`}>{value}</p>
    </div>
  );
}
