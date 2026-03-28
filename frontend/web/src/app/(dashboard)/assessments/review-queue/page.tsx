"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Eye, ClipboardCheck } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TableLoadingSkeleton } from "@/components/loading-skeleton";
import { EmptyState } from "@/components/empty-state";
import { useReviewQueue } from "@/hooks/use-assessments";
import type { ReviewStatus } from "@/types/assessment";

const REVIEW_STATUS_STYLES: Record<ReviewStatus, { label: string; className: string }> = {
  pending: { label: "Pending", className: "bg-slate-100 text-slate-600" },
  accepted: { label: "Accepted", className: "bg-emerald-50 text-emerald-700" },
  modified: { label: "Modified", className: "bg-blue-50 text-blue-700" },
  flagged: { label: "Flagged", className: "bg-red-50 text-red-700" },
};

function formatConfidence(score: number | null): string {
  if (score === null || score === undefined) return "--";
  return `${Math.round(score * 100)}%`;
}

export default function ReviewQueuePage() {
  const router = useRouter();
  const { items, total, isLoading, error } = useReviewQueue();

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
        title="Review Queue"
        description={`${total} item${total !== 1 ? "s" : ""} awaiting review`}
      />

      <div className="space-y-4">
        {isLoading ? (
          <TableLoadingSkeleton rows={5} />
        ) : items.length === 0 ? (
          <EmptyState
            icon={ClipboardCheck}
            title="Review queue is empty"
            description="No responses are pending review at this time."
            actionLabel="Back to Assessments"
            onAction={() => router.push("/assessments")}
          />
        ) : (
          <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Assessment</TableHead>
                  <TableHead>Vendor</TableHead>
                  <TableHead>Question</TableHead>
                  <TableHead className="w-[100px]">Confidence</TableHead>
                  <TableHead className="w-[110px]">Status</TableHead>
                  <TableHead className="w-[80px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item, idx) => {
                  const statusInfo = REVIEW_STATUS_STYLES[item.review_status];
                  return (
                    <TableRow key={item.id || `review-${idx}`}>
                      <TableCell>
                        <span className="font-medium text-text-primary">
                          {item.assessment_title}
                        </span>
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        {item.vendor_name}
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="text-sm text-text-primary line-clamp-1">
                            {item.question_text}
                          </p>
                          <p className="text-xs text-text-muted">
                            {item.question_section}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span
                          className={`text-sm font-medium ${
                            item.confidence_score !== null
                              ? item.confidence_score >= 0.8
                                ? "text-emerald-600"
                                : item.confidence_score >= 0.5
                                ? "text-amber-600"
                                : "text-red-600"
                              : "text-text-muted"
                          }`}
                        >
                          {formatConfidence(item.confidence_score)}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={`${statusInfo.className} border-0`}
                        >
                          {statusInfo.label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            router.push(
                              `/assessments/${item.assessment_id}`
                            )
                          }
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </>
  );
}
