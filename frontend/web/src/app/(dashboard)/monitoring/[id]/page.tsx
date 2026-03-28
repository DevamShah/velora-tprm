"use client";

import React, { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import {
  ArrowLeft,
  Bell,
  CheckCircle2,
  Eye,
  EyeOff,
  Search,
  Building2,
  Clock,
  AlertTriangle,
  ExternalLink,
  Loader2,
  Shield,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { PageLoadingSkeleton } from "@/components/loading-skeleton";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { AlertPriorityBadge } from "@/components/monitoring/alert-priority-badge";
import { AlertStatusBadge } from "@/components/monitoring/alert-status-badge";
import {
  useAlert,
  useAcknowledgeAlert,
  useResolveAlert,
  useSuppressAlert,
} from "@/hooks/use-monitoring";
import { ALERT_SOURCE_LABELS } from "@/types/monitoring";

function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function AlertDetailPage() {
  const router = useRouter();
  const params = useParams();
  const alertId = params.id as string;

  const { alert, isLoading, error, refetch } = useAlert(alertId);
  const { acknowledge, isLoading: acknowledging } = useAcknowledgeAlert();
  const { resolve, isLoading: resolving } = useResolveAlert();
  const { suppress, isLoading: suppressing } = useSuppressAlert();

  const [resolveOpen, setResolveOpen] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState("");

  const anyLoading = acknowledging || resolving || suppressing;

  async function handleAcknowledge() {
    try {
      await acknowledge(alertId);
      toast.success("Alert acknowledged");
      refetch();
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "Failed to acknowledge"
      );
    }
  }

  async function handleResolve() {
    if (!resolutionNotes.trim()) {
      toast.error("Please provide resolution notes");
      return;
    }
    try {
      await resolve(alertId, resolutionNotes);
      toast.success("Alert resolved");
      setResolveOpen(false);
      setResolutionNotes("");
      refetch();
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "Failed to resolve"
      );
    }
  }

  async function handleSuppress() {
    try {
      await suppress(alertId);
      toast.success("Alert suppressed");
      refetch();
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "Failed to suppress"
      );
    }
  }

  if (isLoading) return <PageLoadingSkeleton />;

  if (error || !alert) {
    return (
      <EmptyState
        icon={Bell}
        title="Alert not found"
        description={error || "The requested alert could not be loaded."}
        actionLabel="Back to Monitoring"
        onAction={() => router.push("/monitoring")}
      />
    );
  }

  const canAcknowledge = alert.status === "new";
  const canInvestigate = alert.status === "acknowledged";
  const canResolve =
    alert.status === "new" ||
    alert.status === "acknowledged" ||
    alert.status === "investigating";
  const canSuppress =
    alert.status !== "resolved" && alert.status !== "suppressed";

  return (
    <>
      <div className="flex items-center gap-2 mb-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/monitoring")}
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Monitoring
        </Button>
      </div>

      <PageHeader
        title={alert.title}
        description={alert.vendor_name}
        actions={
          <div className="flex items-center gap-2">
            <AlertPriorityBadge priority={alert.priority} size="md" />
            <AlertStatusBadge status={alert.status} />
          </div>
        }
      />

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center gap-2 mb-6">
        {canAcknowledge && (
          <Button
            size="sm"
            variant="outline"
            onClick={handleAcknowledge}
            disabled={anyLoading}
          >
            {acknowledging ? (
              <Loader2 className="h-4 w-4 mr-1 animate-spin" />
            ) : (
              <Eye className="h-4 w-4 mr-1" />
            )}
            Acknowledge
          </Button>
        )}
        {canResolve && (
          <Button
            size="sm"
            className="bg-emerald-600 hover:bg-emerald-700"
            onClick={() => setResolveOpen(true)}
            disabled={anyLoading}
          >
            {resolving ? (
              <Loader2 className="h-4 w-4 mr-1 animate-spin" />
            ) : (
              <CheckCircle2 className="h-4 w-4 mr-1" />
            )}
            Resolve
          </Button>
        )}
        {canSuppress && (
          <Button
            size="sm"
            variant="outline"
            className="text-text-muted hover:text-text-secondary"
            onClick={handleSuppress}
            disabled={anyLoading}
          >
            {suppressing ? (
              <Loader2 className="h-4 w-4 mr-1 animate-spin" />
            ) : (
              <EyeOff className="h-4 w-4 mr-1" />
            )}
            Suppress
          </Button>
        )}
        <Button
          size="sm"
          variant="outline"
          onClick={() => router.push(`/vendors/${alert.vendor_id}`)}
        >
          <Building2 className="h-4 w-4 mr-1" />
          View Vendor
        </Button>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Main Column */}
        <div className="lg:col-span-2 space-y-4">
          {/* Description */}
          {alert.description && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  Description
                </h3>
                <p className="text-sm text-text-secondary whitespace-pre-wrap">
                  {alert.description}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Impact Assessment */}
          {alert.impact_assessment && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  <AlertTriangle className="h-4 w-4 inline mr-1 text-amber-500" />
                  Impact Assessment
                </h3>
                <p className="text-sm text-text-secondary whitespace-pre-wrap">
                  {alert.impact_assessment}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Recommended Actions */}
          {alert.recommended_actions && alert.recommended_actions.length > 0 && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  Recommended Actions
                </h3>
                <ul className="space-y-2">
                  {alert.recommended_actions.map((action, idx) => (
                    <li
                      key={idx}
                      className="flex items-start gap-2 text-sm text-text-secondary"
                    >
                      <span className="w-5 h-5 rounded-full bg-accent-primary/10 text-accent-primary text-xs flex items-center justify-center shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      {action}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Resolution Notes */}
          {alert.resolution_notes && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  <CheckCircle2 className="h-4 w-4 inline mr-1 text-emerald-500" />
                  Resolution
                </h3>
                <p className="text-sm text-text-secondary whitespace-pre-wrap">
                  {alert.resolution_notes}
                </p>
                {alert.resolved_by && (
                  <p className="text-xs text-text-muted mt-2">
                    Resolved by {alert.resolved_by} on{" "}
                    {formatDateTime(alert.resolved_at)}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Related Alerts */}
          {alert.related_alerts && alert.related_alerts.length > 0 && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  Related Alerts ({alert.related_alerts.length})
                </h3>
                <div className="space-y-2">
                  {alert.related_alerts.map((ra) => (
                    <div
                      key={ra.id}
                      className="flex items-center justify-between p-3 rounded-lg border border-surface-card-border hover:bg-surface-main cursor-pointer transition-colors"
                      onClick={() => router.push(`/monitoring/${ra.id}`)}
                    >
                      <div className="flex items-center gap-2">
                        <AlertPriorityBadge priority={ra.priority} />
                        <span className="text-sm text-text-primary">
                          {ra.title}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <AlertStatusBadge status={ra.status} />
                        <ExternalLink className="h-3.5 w-3.5 text-text-muted" />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-4">
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-sm font-semibold text-text-primary mb-4">
                Details
              </h3>
              <div className="space-y-3">
                <InfoRow
                  icon={Shield}
                  label="Source"
                  value={ALERT_SOURCE_LABELS[alert.source]}
                />
                <InfoRow
                  icon={Building2}
                  label="Vendor"
                  value={alert.vendor_name}
                />
                <InfoRow
                  icon={Clock}
                  label="Created"
                  value={formatDateTime(alert.created_at)}
                />
                <InfoRow
                  icon={Clock}
                  label="Updated"
                  value={formatDateTime(alert.updated_at)}
                />
                {alert.acknowledged_at && (
                  <InfoRow
                    icon={Eye}
                    label="Acknowledged"
                    value={`${formatDateTime(alert.acknowledged_at)}${
                      alert.acknowledged_by
                        ? ` by ${alert.acknowledged_by}`
                        : ""
                    }`}
                  />
                )}
                {alert.resolved_at && (
                  <InfoRow
                    icon={CheckCircle2}
                    label="Resolved"
                    value={`${formatDateTime(alert.resolved_at)}${
                      alert.resolved_by ? ` by ${alert.resolved_by}` : ""
                    }`}
                  />
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Resolve Dialog */}
      <Dialog open={resolveOpen} onOpenChange={setResolveOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Resolve Alert</DialogTitle>
            <DialogDescription>
              Provide resolution notes to close this alert.
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4">
            <label className="text-sm font-medium text-text-primary mb-1.5 block">
              Resolution Notes
            </label>
            <textarea
              className="w-full min-h-[100px] rounded-lg border border-surface-card-border bg-white px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary resize-none"
              placeholder="Describe how this alert was resolved..."
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setResolveOpen(false)}
              disabled={resolving}
            >
              Cancel
            </Button>
            <Button
              className="bg-emerald-600 hover:bg-emerald-700"
              onClick={handleResolve}
              disabled={resolving || !resolutionNotes.trim()}
            >
              {resolving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                  Resolving...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-4 w-4 mr-1" />
                  Resolve
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

function InfoRow({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start gap-3 py-2">
      <Icon className="h-4 w-4 text-text-muted mt-0.5 shrink-0" />
      <div>
        <p className="text-xs text-text-muted">{label}</p>
        <p className="text-sm text-text-primary">{value}</p>
      </div>
    </div>
  );
}
