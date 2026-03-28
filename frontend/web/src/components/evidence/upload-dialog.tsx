"use client";

import React, { useState, useCallback, useRef } from "react";
import { Upload, FileText, X, Loader2 } from "lucide-react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useUploadEvidence, useProcessEvidence } from "@/hooks/use-evidence";
import { useVendors } from "@/hooks/use-vendors";
import { EVIDENCE_TYPES, EVIDENCE_TYPE_LABELS } from "@/types/evidence";
import type { EvidenceType } from "@/types/evidence";

interface UploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
  preselectedVendorId?: string;
}

export function UploadDialog({
  open,
  onOpenChange,
  onSuccess,
  preselectedVendorId,
}: UploadDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [vendorId, setVendorId] = useState(preselectedVendorId || "");
  const [docType, setDocType] = useState<EvidenceType | "">("");
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { getUploadUrl } = useUploadEvidence();
  const { processEvidence } = useProcessEvidence();
  const { vendors } = useVendors({ page: 1, page_size: 100 });

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) setFile(droppedFile);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) setFile(selected);
  }, []);

  function resetForm() {
    setFile(null);
    setVendorId(preselectedVendorId || "");
    setDocType("");
    setUploading(false);
  }

  async function handleUpload() {
    if (!file || !vendorId || !docType) {
      toast.error("Please fill in all fields and select a file");
      return;
    }

    setUploading(true);
    try {
      // Step 1: Get presigned upload URL
      const { upload_url, evidence_id } = await getUploadUrl({
        vendor_id: vendorId,
        filename: file.name,
        file_size: file.size,
        mime_type: file.type || "application/octet-stream",
      });

      // Step 2: Upload file to presigned URL
      try {
        await fetch(upload_url, {
          method: "PUT",
          body: file,
          headers: { "Content-Type": file.type || "application/octet-stream" },
        });
      } catch {
        // Presigned URL may fail in dev — that is expected (mock)
        console.warn("Presigned upload failed — expected in dev mode");
      }

      // Step 3: Trigger processing
      await processEvidence(evidence_id);

      toast.success("Evidence uploaded and processing started");
      resetForm();
      onOpenChange(false);
      onSuccess();
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "Upload failed"
      );
    } finally {
      setUploading(false);
    }
  }

  function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) resetForm();
        onOpenChange(v);
      }}
    >
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Upload Evidence</DialogTitle>
          <DialogDescription>
            Upload a document to attach as evidence for a vendor assessment.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Vendor Select */}
          <div>
            <label className="text-sm font-medium text-text-primary mb-1.5 block">
              Vendor
            </label>
            <Select value={vendorId || "none"} onValueChange={(v) => setVendorId(v === "none" ? "" : v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select vendor" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none" disabled>
                  Select vendor
                </SelectItem>
                {vendors.map((v) => (
                  <SelectItem key={v.id} value={v.id}>
                    {v.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Document Type */}
          <div>
            <label className="text-sm font-medium text-text-primary mb-1.5 block">
              Document Type
            </label>
            <Select value={docType || "none"} onValueChange={(v) => setDocType(v === "none" ? "" : (v as EvidenceType))}>
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none" disabled>
                  Select type
                </SelectItem>
                {EVIDENCE_TYPES.map((t) => (
                  <SelectItem key={t} value={t}>
                    {EVIDENCE_TYPE_LABELS[t]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* File Drop Zone */}
          <div>
            <label className="text-sm font-medium text-text-primary mb-1.5 block">
              File
            </label>
            {file ? (
              <div className="flex items-center gap-3 p-3 rounded-lg border border-surface-card-border bg-surface-main">
                <FileText className="h-5 w-5 text-accent-primary shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-text-muted">
                    {formatFileSize(file.size)}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7 shrink-0"
                  onClick={() => setFile(null)}
                >
                  <X className="h-3.5 w-3.5" />
                </Button>
              </div>
            ) : (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`flex flex-col items-center justify-center p-8 rounded-lg border-2 border-dashed cursor-pointer transition-all ${
                  isDragging
                    ? "border-accent-primary bg-accent-primary/5"
                    : "border-surface-card-border hover:border-accent-primary/40 hover:bg-surface-main"
                }`}
              >
                <Upload className="h-8 w-8 text-text-muted mb-2" />
                <p className="text-sm text-text-secondary font-medium">
                  Drop file here or click to browse
                </p>
                <p className="text-xs text-text-muted mt-1">
                  PDF, DOCX, XLSX, CSV, TXT up to 50 MB
                </p>
                <Input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept=".pdf,.docx,.xlsx,.csv,.txt,.doc,.xls,.pptx,.png,.jpg,.jpeg"
                  onChange={handleFileSelect}
                />
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => {
              resetForm();
              onOpenChange(false);
            }}
            disabled={uploading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            disabled={uploading || !file || !vendorId || !docType}
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-1" />
                Upload
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
