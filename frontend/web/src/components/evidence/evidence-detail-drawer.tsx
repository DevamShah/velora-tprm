"use client";

import React, { useState } from "react";
import {
  X,
  FileText,
  CheckCircle2,
  XCircle,
  Loader2,
  Shield,
  Clock,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { ExtractionViewer } from "@/components/evidence/extraction-viewer";
import { useEvidence, useVerifyMapping } from "@/hooks/use-evidence";
import {
  EVIDENCE_TYPE_LABELS,
  EVIDENCE_STATUS_LABELS,
} from "@/types/evidence";
import type { EvidenceStatus, EvidenceType, EvidenceControlMapping } from "@/types/evidence";

interface EvidenceDetailDrawerProps {
  evidenceId: string | null;
  open: boolean;
  onClose: () => void;
  onMappingUpdated?: () => void;
}

const STATUS_VARIANT: Record<EvidenceStatus, "default" | "secondary" | "outline" | "low" | "critical"> = {
  pending: "outline",
  processing: "default",
  processed: "low",
  failed: "critical",
  archived: "secondary",
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function EvidenceDetailDrawer({
  evidenceId,
  open,
  onClose,
  onMappingUpdated,
}: EvidenceDetailDrawerProps) {
  const { evidence, isLoading, error, refetch } = useEvidence(evidenceId || "");

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-navy-950/30 backdrop-blur-sm z-40 animate-fade-in"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed right-0 top-0 bottom-0 w-full max-w-xl bg-white border-l border-surface-card-border shadow-2xl z-50 flex flex-col animate-slide-in-right overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-surface-card-border shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            <FileText className="h-5 w-5 text-accent-primary shrink-0" />
            <div className="min-w-0">
              <h2 className="text-base font-semibold text-text-primary truncate">
                {isLoading ? "Loading..." : evidence?.filename || "Evidence Detail"}
              </h2>
              {evidence && (
                <p className="text-xs text-text-muted">
                  {evidence.vendor_name} &middot; {formatFileSize(evidence.file_size)}
                </p>
              )}
            </div>
          </div>
          <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-6 space-y-4">
              <Skeleton className="h-8 w-48" />
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
            </div>
          ) : error || !evidence ? (
            <div className="flex flex-col items-center justify-center h-full text-text-muted">
              <FileText className="h-8 w-8 mb-2" />
              <p className="text-sm">{error || "Evidence not found"}</p>
            </div>
          ) : (
            <div className="p-6">
              {/* Meta row */}
              <div className="flex flex-wrap items-center gap-2 mb-6">
                <Badge variant={STATUS_VARIANT[evidence.status]}>
                  {EVIDENCE_STATUS_LABELS[evidence.status]}
                </Badge>
                <Badge variant="outline">
                  {EVIDENCE_TYPE_LABELS[evidence.document_type as EvidenceType] || evidence.document_type}
                </Badge>
                <span className="text-xs text-text-muted flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {formatDate(evidence.created_at)}
                </span>
              </div>

              <Tabs defaultValue="extractions">
                <TabsList>
                  <TabsTrigger value="extractions">
                    Extractions ({evidence.extractions?.length || 0})
                  </TabsTrigger>
                  <TabsTrigger value="mappings">
                    Control Mappings ({evidence.mappings?.length || 0})
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="extractions" className="mt-4">
                  <ExtractionViewer extractions={evidence.extractions || []} />
                </TabsContent>

                <TabsContent value="mappings" className="mt-4">
                  <MappingsList
                    evidenceId={evidence.id}
                    mappings={evidence.mappings || []}
                    onUpdated={() => {
                      refetch();
                      onMappingUpdated?.();
                    }}
                  />
                </TabsContent>
              </Tabs>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

/* --- Control Mappings List --- */

function MappingsList({
  evidenceId,
  mappings,
  onUpdated,
}: {
  evidenceId: string;
  mappings: EvidenceControlMapping[];
  onUpdated: () => void;
}) {
  const { verifyMapping, isLoading: verifyLoading } = useVerifyMapping();
  const [actionId, setActionId] = useState<string | null>(null);

  async function handleVerify(mappingId: string, verified: boolean) {
    setActionId(mappingId);
    try {
      await verifyMapping(evidenceId, mappingId, verified);
      toast.success(verified ? "Mapping verified" : "Mapping rejected");
      onUpdated();
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "Failed to update mapping"
      );
    } finally {
      setActionId(null);
    }
  }

  if (mappings.length === 0) {
    return (
      <div className="text-center py-8 text-text-muted text-sm">
        <Shield className="h-6 w-6 mx-auto mb-2" />
        No control mappings found for this evidence.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {mappings.map((m) => {
        const isActioning = actionId === m.id && verifyLoading;

        return (
          <div
            key={m.id}
            className="p-3 rounded-lg border border-surface-card-border bg-white"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-text-primary">
                    {m.control_name}
                  </span>
                  <Badge variant="outline" className="text-[10px]">
                    {m.framework_name}
                  </Badge>
                </div>
                <div className="flex items-center gap-3 text-xs text-text-muted">
                  <span>
                    Relevance: {Math.round(m.relevance_score * 100)}%
                  </span>
                  {m.verified_at && (
                    <span>Verified: {formatDate(m.verified_at)}</span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-1 shrink-0">
                {m.verification === "verified" ? (
                  <Badge variant="low" className="text-xs">
                    <CheckCircle2 className="h-3 w-3 mr-0.5" />
                    Verified
                  </Badge>
                ) : m.verification === "rejected" ? (
                  <Badge variant="critical" className="text-xs">
                    <XCircle className="h-3 w-3 mr-0.5" />
                    Rejected
                  </Badge>
                ) : (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-7 px-2 text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 border-emerald-200"
                      onClick={() => handleVerify(m.id, true)}
                      disabled={isActioning}
                    >
                      {isActioning ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <CheckCircle2 className="h-3 w-3 mr-0.5" />
                      )}
                      Verify
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-7 px-2 text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
                      onClick={() => handleVerify(m.id, false)}
                      disabled={isActioning}
                    >
                      {isActioning ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <XCircle className="h-3 w-3 mr-0.5" />
                      )}
                      Reject
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
