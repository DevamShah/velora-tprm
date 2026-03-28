"use client";

import React, { useState } from "react";
import {
  FileBarChart,
  Plus,
  Download,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { TableLoadingSkeleton } from "@/components/loading-skeleton";
import { EmptyState } from "@/components/empty-state";
import { useReports, useReportGeneration } from "@/hooks/use-dashboard";
import { REPORT_TEMPLATES, REPORT_STATUS_LABELS } from "@/types/dashboard";
import type { ReportStatus, GenerateReportPayload } from "@/types/dashboard";

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

const STATUS_ICON: Record<ReportStatus, React.ReactNode> = {
  pending: <Clock className="w-3.5 h-3.5 text-text-muted" />,
  generating: <Loader2 className="w-3.5 h-3.5 text-accent-primary animate-spin" />,
  completed: <CheckCircle2 className="w-3.5 h-3.5 text-risk-low" />,
  failed: <XCircle className="w-3.5 h-3.5 text-risk-critical" />,
};

const STATUS_VARIANT: Record<ReportStatus, "secondary" | "default" | "low" | "destructive"> = {
  pending: "secondary",
  generating: "default",
  completed: "low",
  failed: "destructive",
};

export default function ReportsPage() {
  const { reports, isLoading, error, refetch } = useReports();
  const { generateReport, isLoading: isGenerating } = useReportGeneration();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [template, setTemplate] = useState("");
  const [format, setFormat] = useState<"pdf" | "csv">("pdf");
  const [reportName, setReportName] = useState("");

  if (error) {
    toast.error(error);
  }

  const handleGenerate = async () => {
    if (!template) {
      toast.error("Please select a report template");
      return;
    }
    try {
      const payload: GenerateReportPayload = {
        template,
        format,
        name: reportName || undefined,
      };
      await generateReport(payload);
      toast.success("Report generation started");
      setDialogOpen(false);
      setTemplate("");
      setFormat("pdf");
      setReportName("");
      refetch();
    } catch (err) {
      toast.error("Failed to generate report");
    }
  };

  return (
    <>
      <PageHeader
        title="Reports"
        description="Generate and view risk reports"
        actions={
          <Button onClick={() => setDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-1" />
            Generate Report
          </Button>
        }
      />

      <div className="space-y-4">
        {isLoading ? (
          <TableLoadingSkeleton rows={5} />
        ) : reports.length === 0 ? (
          <Card>
            <CardContent className="p-0">
              <EmptyState
                icon={FileBarChart}
                title="No reports generated"
                description="Generate reports to share risk insights with stakeholders."
                actionLabel="Generate Report"
                onAction={() => setDialogOpen(true)}
              />
            </CardContent>
          </Card>
        ) : (
          <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Report Name</TableHead>
                  <TableHead className="w-[150px]">Template</TableHead>
                  <TableHead className="w-[80px]">Format</TableHead>
                  <TableHead className="w-[130px]">Status</TableHead>
                  <TableHead className="w-[160px]">Created</TableHead>
                  <TableHead className="w-[80px]" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell>
                      <span className="font-medium text-text-primary">
                        {report.name}
                      </span>
                    </TableCell>
                    <TableCell className="text-text-secondary text-sm">
                      {REPORT_TEMPLATES.find((t) => t.value === report.template)
                        ?.label || report.template}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="uppercase text-[10px]">
                        {report.format}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1.5">
                        {STATUS_ICON[report.status]}
                        <Badge variant={STATUS_VARIANT[report.status]}>
                          {REPORT_STATUS_LABELS[report.status]}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell className="text-text-secondary text-sm">
                      {formatDate(report.created_at)}
                    </TableCell>
                    <TableCell>
                      {report.status === "completed" && report.file_url && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          asChild
                        >
                          <a
                            href={report.file_url}
                            download
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <Download className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>

      {/* Generate Report Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Generate Report</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Report Name (optional)
              </label>
              <Input
                placeholder="e.g., Q1 2026 Executive Summary"
                value={reportName}
                onChange={(e) => setReportName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Template
              </label>
              <Select value={template} onValueChange={setTemplate}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a template" />
                </SelectTrigger>
                <SelectContent>
                  {REPORT_TEMPLATES.map((t) => (
                    <SelectItem key={t.value} value={t.value}>
                      {t.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Format
              </label>
              <Select
                value={format}
                onValueChange={(v) => setFormat(v as "pdf" | "csv")}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pdf">PDF</SelectItem>
                  <SelectItem value="csv">CSV</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDialogOpen(false)}
              disabled={isGenerating}
            >
              Cancel
            </Button>
            <Button onClick={handleGenerate} disabled={isGenerating || !template}>
              {isGenerating && <Loader2 className="w-4 h-4 mr-1 animate-spin" />}
              Generate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
