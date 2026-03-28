"use client";

import React, { useState, useCallback } from "react";
import { Upload, FileText, AlertCircle, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { useBulkImport } from "@/hooks/use-vendors";
import type { BulkImportResponse } from "@/types/vendor";

interface BulkImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

function parsePreviewRows(csv: string): string[][] {
  const lines = csv.trim().split("\n").slice(0, 6);
  return lines.map((line) => line.split(",").map((c) => c.trim()));
}

export function BulkImportDialog({
  open,
  onOpenChange,
  onSuccess,
}: BulkImportDialogProps) {
  const [csvText, setCsvText] = useState("");
  const [result, setResult] = useState<BulkImportResponse | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const { bulkImport, isLoading } = useBulkImport();

  const preview = csvText ? parsePreviewRows(csvText) : [];

  const handleFile = useCallback((file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      setCsvText(text);
      setResult(null);
    };
    reader.readAsText(file);
  }, []);

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith(".csv")) {
      handleFile(file);
    } else {
      toast.error("Please drop a CSV file");
    }
  }

  function handleFileInput(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  async function handleImport() {
    if (!csvText.trim()) {
      toast.error("No CSV data provided");
      return;
    }
    try {
      const res = await bulkImport(csvText);
      setResult(res);
      if (res.success_count > 0) {
        toast.success(`Imported ${res.success_count} vendors`);
        onSuccess();
      }
      if (res.error_count > 0) {
        toast.error(`${res.error_count} rows failed`);
      }
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "Import failed"
      );
    }
  }

  function handleClose(val: boolean) {
    if (!val) {
      setCsvText("");
      setResult(null);
    }
    onOpenChange(val);
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Bulk Import Vendors</DialogTitle>
          <DialogDescription>
            Upload a CSV file or paste CSV data to import vendors.
          </DialogDescription>
        </DialogHeader>

        {!result ? (
          <div className="space-y-4">
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                dragActive
                  ? "border-accent-primary bg-accent-primary/5"
                  : "border-surface-card-border"
              }`}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
            >
              <Upload className="mx-auto h-8 w-8 text-text-muted mb-3" />
              <p className="text-sm text-text-secondary mb-2">
                Drag and drop a CSV file here
              </p>
              <label className="cursor-pointer">
                <span className="text-sm text-accent-primary hover:underline">
                  or browse files
                </span>
                <input
                  type="file"
                  accept=".csv"
                  className="hidden"
                  onChange={handleFileInput}
                />
              </label>
            </div>

            <div>
              <label className="text-sm font-medium text-text-primary block mb-1.5">
                Or paste CSV data
              </label>
              <textarea
                className="w-full h-32 rounded-lg border border-surface-card-border bg-white px-3 py-2 text-sm text-text-primary font-mono placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary transition-all resize-none"
                placeholder="name,domain,industry&#10;Acme Corp,acme.com,Technology"
                value={csvText}
                onChange={(e) => { setCsvText(e.target.value); setResult(null); }}
              />
            </div>

            {preview.length > 0 && (
              <div>
                <p className="text-xs font-medium text-text-muted mb-2">
                  Preview (first {Math.min(preview.length, 6)} rows)
                </p>
                <div className="overflow-x-auto rounded-lg border border-surface-card-border">
                  <table className="w-full text-xs">
                    <tbody>
                      {preview.map((row, i) => (
                        <tr
                          key={i}
                          className={i === 0 ? "bg-surface-main font-medium" : ""}
                        >
                          {row.map((cell, j) => (
                            <td key={j} className="px-3 py-1.5 border-b border-surface-card-border">
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-6">
              {result.success_count > 0 && (
                <div className="flex items-center gap-2 text-risk-low">
                  <CheckCircle2 className="h-5 w-5" />
                  <span className="text-sm font-medium">
                    {result.success_count} imported
                  </span>
                </div>
              )}
              {result.error_count > 0 && (
                <div className="flex items-center gap-2 text-risk-critical">
                  <AlertCircle className="h-5 w-5" />
                  <span className="text-sm font-medium">
                    {result.error_count} failed
                  </span>
                </div>
              )}
            </div>
            {result.errors.length > 0 && (
              <div className="rounded-lg border border-risk-critical/20 bg-risk-critical/5 p-3 max-h-40 overflow-y-auto">
                <p className="text-xs font-medium text-risk-critical mb-2">Errors:</p>
                {result.errors.map((err, i) => (
                  <p key={i} className="text-xs text-text-secondary">
                    Row {err.row}: {err.message}
                  </p>
                ))}
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => handleClose(false)}>
            {result ? "Close" : "Cancel"}
          </Button>
          {!result && (
            <Button onClick={handleImport} disabled={isLoading || !csvText.trim()}>
              <FileText className="h-4 w-4 mr-1" />
              {isLoading ? "Importing..." : "Import"}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
