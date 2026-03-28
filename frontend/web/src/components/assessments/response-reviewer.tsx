"use client";

import React, { useState } from "react";
import { Check, Flag, MessageSquare, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useUpdateResponse } from "@/hooks/use-assessments";
import type { AssessmentResponse, ReviewStatus } from "@/types/assessment";

const REVIEW_STATUS_STYLES: Record<ReviewStatus, { label: string; className: string }> = {
  pending: { label: "Pending Review", className: "bg-slate-100 text-slate-600" },
  accepted: { label: "Accepted", className: "bg-emerald-50 text-emerald-700" },
  modified: { label: "Modified", className: "bg-blue-50 text-blue-700" },
  flagged: { label: "Flagged", className: "bg-red-50 text-red-700" },
};

interface ResponseReviewerProps {
  assessmentId: string;
  response: AssessmentResponse;
  onUpdated: () => void;
}

export function ResponseReviewer({ assessmentId, response, onUpdated }: ResponseReviewerProps) {
  const { updateResponse, isLoading } = useUpdateResponse();
  const [notes, setNotes] = useState(response.reviewer_notes || "");
  const [showNotes, setShowNotes] = useState(!!response.reviewer_notes);

  const statusInfo = REVIEW_STATUS_STYLES[response.review_status];

  async function handleReview(status: ReviewStatus) {
    try {
      await updateResponse(assessmentId, response.id, {
        review_status: status,
        reviewer_notes: notes || undefined,
      });
      toast.success(`Response ${status === "accepted" ? "accepted" : "flagged"}`);
      onUpdated();
    } catch (err) {
      toast.error((err as { message?: string }).message || "Failed to update review");
    }
  }

  return (
    <div className="border border-surface-card-border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-text-muted uppercase tracking-wider">
          Review Status
        </span>
        <Badge variant="outline" className={`${statusInfo.className} border-0`}>
          {statusInfo.label}
        </Badge>
      </div>

      {response.confidence_score !== null && (
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-muted">Confidence Score</span>
          <span className="text-sm font-medium text-text-primary">
            {Math.round(response.confidence_score * 100)}%
          </span>
        </div>
      )}

      {showNotes ? (
        <div>
          <label className="text-xs font-medium text-text-muted block mb-1">
            Reviewer Notes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add notes about this response..."
            className="w-full min-h-[80px] px-3 py-2 text-sm rounded-lg border border-surface-card-border bg-white text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary resize-y"
          />
        </div>
      ) : (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowNotes(true)}
          className="text-text-muted"
        >
          <MessageSquare className="h-3 w-3 mr-1" />
          Add Notes
        </Button>
      )}

      <div className="flex items-center gap-2 pt-1">
        <Button
          size="sm"
          onClick={() => handleReview("accepted")}
          disabled={isLoading}
          className="bg-emerald-600 hover:bg-emerald-700 text-white"
        >
          {isLoading ? (
            <Loader2 className="h-3 w-3 mr-1 animate-spin" />
          ) : (
            <Check className="h-3 w-3 mr-1" />
          )}
          Accept
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => handleReview("flagged")}
          disabled={isLoading}
          className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
        >
          {isLoading ? (
            <Loader2 className="h-3 w-3 mr-1 animate-spin" />
          ) : (
            <Flag className="h-3 w-3 mr-1" />
          )}
          Flag
        </Button>
      </div>

      {response.reviewed_at && (
        <p className="text-xs text-text-muted">
          Last reviewed:{" "}
          {new Date(response.reviewed_at).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
            hour: "numeric",
            minute: "2-digit",
          })}
        </p>
      )}
    </div>
  );
}

export { REVIEW_STATUS_STYLES };
