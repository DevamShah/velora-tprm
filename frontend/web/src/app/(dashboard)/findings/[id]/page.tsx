"use client";

import React, { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  AlertTriangle,
  CheckCircle2,
  Plus,
  Loader2,
  Clock,
  Shield,
  Building2,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { FindingSeverityBadge } from "@/components/findings/finding-severity-badge";
import { FindingStatusBadge } from "@/components/findings/finding-status-badge";
import {
  useFinding,
  useCloseFinding,
  useAddRemediation,
  useUpdateRemediation,
} from "@/hooks/use-findings";
import { REMEDIATION_STATUS_LABELS } from "@/types/finding";
import type {
  RemediationStatus,
  CreateRemediationPayload,
} from "@/types/finding";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

const REMEDIATION_STATUS_STYLES: Record<RemediationStatus, string> = {
  planned: "bg-gray-100 text-gray-700",
  in_progress: "bg-blue-50 text-blue-700",
  completed: "bg-green-50 text-green-700",
  verified: "bg-purple-50 text-purple-700",
  overdue: "bg-red-50 text-red-700",
};

export default function FindingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const { finding, isLoading, error, refetch } = useFinding(id);
  const { closeFinding, isLoading: isClosing } = useCloseFinding();
  const { addRemediation, isLoading: isAdding } = useAddRemediation();
  const { updateRemediation, isLoading: isUpdating } = useUpdateRemediation();

  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newRemediation, setNewRemediation] = useState<CreateRemediationPayload>({
    title: "",
    description: "",
    due_date: "",
  });

  if (error) {
    toast.error(error);
  }

  if (isLoading) {
    return <FindingDetailSkeleton />;
  }

  if (!finding) {
    return (
      <>
        <PageHeader title="Finding Details" />
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <AlertTriangle className="w-8 h-8 text-text-muted mb-3" />
          <p className="text-sm text-text-muted">Finding not found</p>
          <Button
            variant="outline"
            size="sm"
            className="mt-4"
            onClick={() => router.push("/findings")}
          >
            <ArrowLeft className="w-3.5 h-3.5 mr-1" />
            Back to Findings
          </Button>
        </div>
      </>
    );
  }

  const handleClose = async () => {
    try {
      await closeFinding(id);
      toast.success("Finding closed");
      refetch();
    } catch {
      toast.error("Failed to close finding");
    }
  };

  const handleAddRemediation = async () => {
    if (!newRemediation.title) {
      toast.error("Title is required");
      return;
    }
    try {
      await addRemediation(id, newRemediation);
      toast.success("Remediation action added");
      setAddDialogOpen(false);
      setNewRemediation({ title: "", description: "", due_date: "" });
      refetch();
    } catch {
      toast.error("Failed to add remediation");
    }
  };

  const handleStatusUpdate = async (
    actionId: string,
    status: RemediationStatus
  ) => {
    try {
      await updateRemediation(id, actionId, { status });
      toast.success("Status updated");
      refetch();
    } catch {
      toast.error("Failed to update status");
    }
  };

  const canClose = finding.status !== "closed" && finding.status !== "false_positive";

  return (
    <>
      <PageHeader
        title={finding.title}
        description={`Finding for ${finding.vendor_name}`}
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/findings")}
            >
              <ArrowLeft className="w-3.5 h-3.5 mr-1" />
              Back
            </Button>
            {canClose && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleClose}
                disabled={isClosing}
                className="text-risk-low hover:text-risk-low"
              >
                {isClosing ? (
                  <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                ) : (
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                )}
                Close Finding
              </Button>
            )}
          </div>
        }
      />

      <div className="grid gap-4 lg:grid-cols-3 mb-6">
        {/* Metadata */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-3">
              <FindingSeverityBadge severity={finding.severity} size="md" />
              <FindingStatusBadge status={finding.status} />
            </div>
            {finding.description && (
              <div>
                <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-1">
                  Description
                </p>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {finding.description}
                </p>
              </div>
            )}
            {finding.affected_controls && finding.affected_controls.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
                  Affected Controls
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {finding.affected_controls.map((control, idx) => {
                    const label = typeof control === "string"
                      ? control
                      : (control as Record<string, unknown>).name || (control as Record<string, unknown>).id || JSON.stringify(control);
                    return (
                      <Badge key={String(label) + idx} variant="outline" className="text-xs">
                        <Shield className="w-3 h-3 mr-1" />
                        {String(label)}
                      </Badge>
                    );
                  })}
                </div>
              </div>
            )}
            {finding.remediation_guidance && (
              <div>
                <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-1">
                  Remediation Guidance
                </p>
                <div className="rounded-lg bg-surface-main/60 p-3 text-sm text-text-secondary leading-relaxed">
                  <RemediationGuidanceContent guidance={finding.remediation_guidance} />
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Sidebar info */}
        <div className="space-y-4">
          <Card>
            <CardContent className="pt-5 space-y-3">
              <InfoRow label="Vendor" icon={Building2}>
                {finding.vendor_name}
              </InfoRow>
              <InfoRow label="Assigned To" icon={Shield}>
                {finding.assigned_to || "Unassigned"}
              </InfoRow>
              <InfoRow label="SLA Due" icon={Clock}>
                {formatDate(finding.sla_due_date)}
              </InfoRow>
              <InfoRow label="Created" icon={Clock}>
                {formatDate(finding.created_at)}
              </InfoRow>
              <InfoRow label="Updated" icon={Clock}>
                {formatDate(finding.updated_at)}
              </InfoRow>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Remediation Actions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Remediation Actions</CardTitle>
            <Button size="sm" onClick={() => setAddDialogOpen(true)}>
              <Plus className="w-3.5 h-3.5 mr-1" />
              Add Action
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {finding.remediation_actions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <p className="text-sm text-text-muted">
                No remediation actions yet. Add one to start tracking progress.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {finding.remediation_actions.map((action) => (
                <div
                  key={action.id}
                  className="flex items-start gap-3 p-3 rounded-lg border border-surface-card-border hover:bg-surface-main/30 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-text-primary">
                      {action.title}
                    </p>
                    {action.description && (
                      <p className="text-xs text-text-muted mt-0.5">
                        {action.description}
                      </p>
                    )}
                    <div className="flex items-center gap-3 mt-2">
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                          REMEDIATION_STATUS_STYLES[action.status]
                        }`}
                      >
                        {REMEDIATION_STATUS_LABELS[action.status]}
                      </span>
                      {action.due_date && (
                        <span className="text-xs text-text-muted">
                          Due: {formatDate(action.due_date)}
                        </span>
                      )}
                      {action.assigned_to && (
                        <span className="text-xs text-text-muted">
                          Assigned: {action.assigned_to}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    {action.status === "planned" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs"
                        onClick={() =>
                          handleStatusUpdate(action.id, "in_progress")
                        }
                        disabled={isUpdating}
                      >
                        Start
                      </Button>
                    )}
                    {action.status === "in_progress" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs"
                        onClick={() =>
                          handleStatusUpdate(action.id, "completed")
                        }
                        disabled={isUpdating}
                      >
                        Complete
                      </Button>
                    )}
                    {action.status === "completed" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs"
                        onClick={() =>
                          handleStatusUpdate(action.id, "verified")
                        }
                        disabled={isUpdating}
                      >
                        Verify
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Remediation Dialog */}
      <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Add Remediation Action</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Title
              </label>
              <Input
                placeholder="e.g., Update firewall rules"
                value={newRemediation.title}
                onChange={(e) =>
                  setNewRemediation((prev) => ({
                    ...prev,
                    title: e.target.value,
                  }))
                }
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Description (optional)
              </label>
              <Input
                placeholder="Details about this action"
                value={newRemediation.description || ""}
                onChange={(e) =>
                  setNewRemediation((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Due Date (optional)
              </label>
              <Input
                type="date"
                value={newRemediation.due_date || ""}
                onChange={(e) =>
                  setNewRemediation((prev) => ({
                    ...prev,
                    due_date: e.target.value,
                  }))
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setAddDialogOpen(false)}
              disabled={isAdding}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAddRemediation}
              disabled={isAdding || !newRemediation.title}
            >
              {isAdding && <Loader2 className="w-4 h-4 mr-1 animate-spin" />}
              Add Action
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function RemediationGuidanceContent({ guidance }: { guidance: any }) {
  if (typeof guidance === "string") {
    return <>{guidance}</>;
  }

  const g = guidance as Record<string, string | string[]>;
  return (
    <div className="space-y-2">
      {g.risk_impact && (
        <div>
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider">Risk Impact</p>
          <p>{String(g.risk_impact)}</p>
        </div>
      )}
      {g.recommendation && (
        <div>
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider">Recommendation</p>
          <p>{String(g.recommendation)}</p>
        </div>
      )}
      {g.affected_controls && Array.isArray(g.affected_controls) && (
        <div>
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider">Controls</p>
          <div className="flex flex-wrap gap-1 mt-1">
            {(g.affected_controls as string[]).map((c, i) => (
              <Badge key={i} variant="outline" className="text-xs">
                {String(c)}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function InfoRow({
  label,
  icon: Icon,
  children,
}: {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-2">
      <Icon className="w-3.5 h-3.5 text-text-muted shrink-0" />
      <span className="text-xs text-text-muted w-20 shrink-0">{label}</span>
      <span className="text-sm text-text-primary font-medium truncate">
        {children}
      </span>
    </div>
  );
}

function FindingDetailSkeleton() {
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-48" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-9 w-20" />
          <Skeleton className="h-9 w-32" />
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Skeleton className="h-64 rounded-xl lg:col-span-2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
      <Skeleton className="h-48 rounded-xl" />
    </div>
  );
}
