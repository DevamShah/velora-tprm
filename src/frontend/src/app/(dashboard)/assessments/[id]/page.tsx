"use client";

import React, { useState, useMemo } from "react";
import { useRouter, useParams } from "next/navigation";
import {
  ArrowLeft,
  Send,
  PlayCircle,
  CheckCircle2,
  XCircle,
  Building2,
  Calendar,
  ClipboardCheck,
  AlertTriangle,
  Loader2,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { PageLoadingSkeleton } from "@/components/loading-skeleton";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { AssessmentStatusBadge } from "@/components/assessments/assessment-status-badge";
import { QuestionRenderer } from "@/components/assessments/question-renderer";
import { ResponseReviewer } from "@/components/assessments/response-reviewer";
import {
  useAssessment,
  useDistributeAssessment,
  useSubmitAssessment,
  useStartReview,
  useCompleteAssessment,
  useCancelAssessment,
} from "@/hooks/use-assessments";
import { useAutoFill } from "@/hooks/use-ai";
import type { AssessmentDetail, AssessmentResponse, AssessmentStatus } from "@/types/assessment";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

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

export default function AssessmentDetailPage() {
  const router = useRouter();
  const params = useParams();
  const assessmentId = params.id as string;

  const { assessment, isLoading, error, refetch } = useAssessment(assessmentId);
  const { distribute, isLoading: distributing } = useDistributeAssessment();
  const { submit, isLoading: submitting } = useSubmitAssessment();
  const { startReview, isLoading: startingReview } = useStartReview();
  const { complete, isLoading: completing } = useCompleteAssessment();
  const { cancel, isLoading: cancelling } = useCancelAssessment();
  const { autoFill, isLoading: autoFilling } = useAutoFill();

  async function handleAction(
    action: (id: string) => Promise<void>,
    label: string
  ) {
    try {
      await action(assessmentId);
      toast.success(`Assessment ${label} successfully`);
      refetch();
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || `Failed to ${label} assessment`
      );
    }
  }

  async function handleAutoFill() {
    try {
      const result = await autoFill(assessmentId);
      toast.success(
        `AI Auto-Fill complete: ${result.filled_count} answers filled (avg confidence ${Math.round(result.confidence_avg * 100)}%)`
      );
      refetch();
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "AI Auto-Fill failed"
      );
    }
  }

  if (isLoading) return <PageLoadingSkeleton />;

  if (error || !assessment) {
    return (
      <EmptyState
        icon={ClipboardCheck}
        title="Assessment not found"
        description={error || "The requested assessment could not be loaded."}
        actionLabel="Back to Assessments"
        onAction={() => router.push("/assessments")}
      />
    );
  }

  const anyActionLoading =
    distributing || submitting || startingReview || completing || cancelling || autoFilling;

  const canAutoFill =
    assessment.status === "draft" ||
    assessment.status === "distributed" ||
    assessment.status === "in_progress";

  return (
    <>
      <div className="flex items-center gap-2 mb-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/assessments")}
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Assessments
        </Button>
      </div>

      <PageHeader
        title={assessment.title}
        description={assessment.vendor?.name || assessment.vendor_name}
        actions={
          <div className="flex items-center gap-2">
            <AssessmentStatusBadge status={assessment.status} />
            {canAutoFill && (
              <Button
                size="sm"
                variant="outline"
                onClick={handleAutoFill}
                disabled={anyActionLoading}
                className="border-purple-200 text-purple-700 hover:bg-purple-50 hover:text-purple-800"
              >
                {autoFilling ? (
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4 mr-1" />
                )}
                AI Auto-Fill
              </Button>
            )}
            <ActionButtons
              status={assessment.status}
              loading={anyActionLoading}
              onDistribute={() => handleAction(distribute, "distributed")}
              onSubmit={() => handleAction(submit, "submitted")}
              onStartReview={() => handleAction(startReview, "review started")}
              onComplete={() => handleAction(complete, "completed")}
              onCancel={() => handleAction(cancel, "cancelled")}
            />
          </div>
        }
      />

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="questionnaire">
            Questionnaire ({assessment.responses?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="findings">Findings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <OverviewTab assessment={assessment} />
        </TabsContent>

        <TabsContent value="questionnaire">
          <QuestionnaireTab
            assessment={assessment}
            onUpdated={refetch}
          />
        </TabsContent>

        <TabsContent value="findings">
          <EmptyState
            icon={AlertTriangle}
            title="No findings yet"
            description="Findings will appear here once the assessment review is complete."
          />
        </TabsContent>
      </Tabs>
    </>
  );
}

/* --- Action Buttons --- */

function ActionButtons({
  status,
  loading,
  onDistribute,
  onSubmit,
  onStartReview,
  onComplete,
  onCancel,
}: {
  status: AssessmentStatus;
  loading: boolean;
  onDistribute: () => void;
  onSubmit: () => void;
  onStartReview: () => void;
  onComplete: () => void;
  onCancel: () => void;
}) {
  const cancelableStatuses: AssessmentStatus[] = [
    "draft",
    "distributed",
    "in_progress",
    "submitted",
    "under_review",
  ];

  return (
    <>
      {status === "draft" && (
        <Button size="sm" onClick={onDistribute} disabled={loading}>
          {loading ? (
            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
          ) : (
            <Send className="h-4 w-4 mr-1" />
          )}
          Distribute
        </Button>
      )}
      {(status === "distributed" || status === "in_progress") && (
        <Button size="sm" onClick={onSubmit} disabled={loading}>
          {loading ? (
            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
          ) : (
            <CheckCircle2 className="h-4 w-4 mr-1" />
          )}
          Mark as Submitted
        </Button>
      )}
      {status === "submitted" && (
        <Button size="sm" onClick={onStartReview} disabled={loading}>
          {loading ? (
            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
          ) : (
            <PlayCircle className="h-4 w-4 mr-1" />
          )}
          Start Review
        </Button>
      )}
      {status === "under_review" && (
        <Button
          size="sm"
          onClick={onComplete}
          disabled={loading}
          className="bg-emerald-600 hover:bg-emerald-700"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
          ) : (
            <CheckCircle2 className="h-4 w-4 mr-1" />
          )}
          Complete
        </Button>
      )}
      {cancelableStatuses.includes(status) && (
        <Button
          variant="outline"
          size="sm"
          onClick={onCancel}
          disabled={loading}
          className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
          ) : (
            <XCircle className="h-4 w-4 mr-1" />
          )}
          Cancel
        </Button>
      )}
    </>
  );
}

/* --- Overview Tab --- */

const STATUS_TIMELINE: AssessmentStatus[] = [
  "draft",
  "distributed",
  "in_progress",
  "submitted",
  "under_review",
  "completed",
];

function OverviewTab({ assessment }: { assessment: AssessmentDetail }) {
  const currentIdx = STATUS_TIMELINE.indexOf(assessment.status);
  const isCancelled = assessment.status === "cancelled";

  // Calculate response completion
  const totalResponses = assessment.responses?.length || 0;
  const answeredResponses =
    assessment.responses?.filter((r) => r.response_value !== null).length || 0;
  const completionPct =
    totalResponses > 0 ? Math.round((answeredResponses / totalResponses) * 100) : 0;

  // Calculate review progress
  const reviewedResponses =
    assessment.responses?.filter(
      (r) => r.review_status === "accepted" || r.review_status === "flagged"
    ).length || 0;
  const reviewPct =
    totalResponses > 0 ? Math.round((reviewedResponses / totalResponses) * 100) : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2 space-y-4">
        {/* Status Timeline */}
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-sm font-semibold text-text-primary mb-4">
              Assessment Progress
            </h3>
            {isCancelled ? (
              <div className="flex items-center gap-2 text-red-600">
                <XCircle className="h-5 w-5" />
                <span className="text-sm font-medium">
                  This assessment has been cancelled
                </span>
              </div>
            ) : (
              <div className="flex items-center gap-1">
                {STATUS_TIMELINE.map((status, idx) => {
                  const isCompleted = idx <= currentIdx;
                  const isCurrent = idx === currentIdx;
                  return (
                    <React.Fragment key={status}>
                      <div className="flex flex-col items-center gap-1 flex-1">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium transition-all ${
                            isCompleted
                              ? isCurrent
                                ? "bg-accent-primary text-white"
                                : "bg-emerald-100 text-emerald-700"
                              : "bg-surface-main text-text-muted"
                          }`}
                        >
                          {isCompleted && !isCurrent ? (
                            <CheckCircle2 className="h-4 w-4" />
                          ) : (
                            idx + 1
                          )}
                        </div>
                        <span
                          className={`text-[10px] text-center leading-tight ${
                            isCurrent
                              ? "text-accent-primary font-medium"
                              : "text-text-muted"
                          }`}
                        >
                          {status.replace("_", " ")}
                        </span>
                      </div>
                      {idx < STATUS_TIMELINE.length - 1 && (
                        <div
                          className={`h-0.5 flex-1 mt-[-16px] ${
                            idx < currentIdx
                              ? "bg-emerald-300"
                              : "bg-surface-card-border"
                          }`}
                        />
                      )}
                    </React.Fragment>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Completion Stats */}
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-sm font-semibold text-text-primary mb-4">
              Completion
            </h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between text-sm mb-1.5">
                  <span className="text-text-secondary">Responses</span>
                  <span className="font-medium text-text-primary">
                    {answeredResponses}/{totalResponses} ({completionPct}%)
                  </span>
                </div>
                <Progress value={completionPct} />
              </div>
              <div>
                <div className="flex items-center justify-between text-sm mb-1.5">
                  <span className="text-text-secondary">Reviews</span>
                  <span className="font-medium text-text-primary">
                    {reviewedResponses}/{totalResponses} ({reviewPct}%)
                  </span>
                </div>
                <Progress value={reviewPct} />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Vendor Info */}
        {assessment.vendor && (
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-sm font-semibold text-text-primary mb-4">
                Vendor Information
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-1">
                <InfoRow
                  icon={Building2}
                  label="Vendor"
                  value={assessment.vendor.name}
                />
                {assessment.vendor.domain && (
                  <InfoRow
                    icon={Building2}
                    label="Domain"
                    value={assessment.vendor.domain}
                  />
                )}
                <InfoRow
                  icon={Building2}
                  label="Tier"
                  value={assessment.vendor.tier || "--"}
                />
                <InfoRow
                  icon={Building2}
                  label="Status"
                  value={assessment.vendor.status || "--"}
                />
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Right column */}
      <div className="space-y-4">
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-sm font-semibold text-text-primary mb-4">
              Details
            </h3>
            <div className="space-y-3">
              <InfoRow
                icon={ClipboardCheck}
                label="Template"
                value={assessment.template?.name || assessment.template_name || "--"}
              />
              <InfoRow
                icon={Calendar}
                label="Due Date"
                value={formatDate(assessment.due_date)}
              />
              <InfoRow
                icon={Calendar}
                label="Created"
                value={formatDateTime(assessment.created_at)}
              />
              {assessment.distributed_at && (
                <InfoRow
                  icon={Send}
                  label="Distributed"
                  value={formatDateTime(assessment.distributed_at)}
                />
              )}
              {assessment.submitted_at && (
                <InfoRow
                  icon={CheckCircle2}
                  label="Submitted"
                  value={formatDateTime(assessment.submitted_at)}
                />
              )}
              {assessment.completed_at && (
                <InfoRow
                  icon={CheckCircle2}
                  label="Completed"
                  value={formatDateTime(assessment.completed_at)}
                />
              )}
            </div>
          </CardContent>
        </Card>

        {assessment.score !== null && (
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-sm font-semibold text-text-primary mb-3">
                Score
              </h3>
              <div className="text-center">
                <span
                  className={`text-4xl font-bold ${
                    assessment.score >= 80
                      ? "text-emerald-600"
                      : assessment.score >= 60
                      ? "text-amber-600"
                      : "text-red-600"
                  }`}
                >
                  {Math.round(assessment.score)}%
                </span>
                <p className="text-xs text-text-muted mt-1">Overall Score</p>
              </div>
            </CardContent>
          </Card>
        )}

        {assessment.description && (
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-sm font-semibold text-text-primary mb-2">
                Description
              </h3>
              <p className="text-sm text-text-secondary whitespace-pre-wrap">
                {assessment.description}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
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

/* --- Questionnaire Tab --- */

function QuestionnaireTab({
  assessment,
  onUpdated,
}: {
  assessment: AssessmentDetail;
  onUpdated: () => void;
}) {
  const responses = assessment.responses || [];
  const [selectedId, setSelectedId] = useState<string | null>(
    responses.length > 0 ? responses[0].id : null
  );

  const isReviewMode =
    assessment.status === "under_review" || assessment.status === "completed";

  // Group responses by section
  const sections = useMemo(() => {
    const map = new Map<string, AssessmentResponse[]>();
    for (const r of responses) {
      const section = r.question?.section || "General";
      if (!map.has(section)) map.set(section, []);
      map.get(section)!.push(r);
    }
    return map;
  }, [responses]);

  const selectedResponse = responses.find((r) => r.id === selectedId);

  if (responses.length === 0) {
    return (
      <EmptyState
        icon={ClipboardCheck}
        title="No questions"
        description="This assessment has no questions yet."
      />
    );
  }

  // Completion stats
  const answered = responses.filter((r) => r.response_value !== null).length;
  const completionPct = Math.round((answered / responses.length) * 100);

  return (
    <div className="space-y-4">
      {/* Completion bar */}
      <div className="flex items-center gap-4 px-1">
        <Progress value={completionPct} className="flex-1" />
        <span className="text-sm text-text-muted whitespace-nowrap">
          {answered}/{responses.length} answered ({completionPct}%)
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Question list */}
        <div className="lg:col-span-1 space-y-2 max-h-[600px] overflow-y-auto pr-1">
          {Array.from(sections.entries()).map(([section, items]) => (
            <div key={section}>
              <p className="text-xs font-semibold text-text-muted uppercase tracking-wider px-2 py-1.5">
                {section}
              </p>
              {items.map((r, idx) => {
                const isSelected = selectedId === r.id;
                const hasResponse = r.response_value !== null;
                const reviewColor =
                  r.review_status === "accepted"
                    ? "border-l-emerald-500"
                    : r.review_status === "flagged"
                    ? "border-l-red-500"
                    : r.review_status === "modified"
                    ? "border-l-blue-500"
                    : "border-l-transparent";

                return (
                  <button
                    key={r.id}
                    onClick={() => setSelectedId(r.id)}
                    className={`w-full text-left p-3 rounded-lg border-l-[3px] transition-all duration-150 ${reviewColor} ${
                      isSelected
                        ? "bg-accent-primary/5 border border-accent-primary/20"
                        : "bg-white border border-surface-card-border hover:bg-surface-main"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p
                        className={`text-sm leading-snug ${
                          isSelected
                            ? "text-text-primary font-medium"
                            : "text-text-secondary"
                        } line-clamp-2`}
                      >
                        {r.question?.question_text || `Question ${idx + 1}`}
                      </p>
                      <div className="flex items-center gap-1 shrink-0">
                        {hasResponse && (
                          <div className="w-2 h-2 rounded-full bg-emerald-400" />
                        )}
                        <ChevronRight
                          className={`h-3 w-3 text-text-muted transition-transform ${
                            isSelected ? "rotate-90" : ""
                          }`}
                        />
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge
                        variant="outline"
                        className="text-[10px] px-1.5 py-0"
                      >
                        {r.question?.question_type?.replace("_", " ") || "text"}
                      </Badge>
                      {r.question?.required && (
                        <span className="text-[10px] text-red-400">
                          Required
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        {/* Answer panel */}
        <div className="lg:col-span-2">
          {selectedResponse ? (
            <Card>
              <CardContent className="pt-6 space-y-6">
                {/* Question header */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="outline" className="text-xs">
                      {selectedResponse.question?.section || "General"}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {selectedResponse.question?.question_type?.replace(
                        "_",
                        " "
                      ) || "text"}
                    </Badge>
                    {selectedResponse.question?.required && (
                      <Badge variant="destructive" className="text-xs">
                        Required
                      </Badge>
                    )}
                  </div>
                  <h3 className="text-base font-medium text-text-primary">
                    {selectedResponse.question?.question_text || "Question"}
                  </h3>
                </div>

                {/* Response */}
                <div>
                  <p className="text-xs font-medium text-text-muted uppercase tracking-wider mb-2">
                    Response
                  </p>
                  <QuestionRenderer
                    question={selectedResponse.question}
                    value={selectedResponse.response_value}
                  />
                </div>

                {/* Metadata */}
                {selectedResponse.responded_at && (
                  <p className="text-xs text-text-muted">
                    Responded: {formatDateTime(selectedResponse.responded_at)}
                  </p>
                )}

                {/* Review panel */}
                {isReviewMode && (
                  <div>
                    <p className="text-xs font-medium text-text-muted uppercase tracking-wider mb-2">
                      Review
                    </p>
                    <ResponseReviewer
                      assessmentId={assessment.id}
                      response={selectedResponse}
                      onUpdated={onUpdated}
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-64 text-text-muted text-sm">
                Select a question from the list to view its response
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
