"use client";

import React from "react";
import { AlertTriangle } from "lucide-react";
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
import { useDeleteVendor } from "@/hooks/use-vendors";

interface DeleteVendorDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  vendorId: string;
  vendorName: string;
  onDeleted: () => void;
}

export function DeleteVendorDialog({
  open,
  onOpenChange,
  vendorId,
  vendorName,
  onDeleted,
}: DeleteVendorDialogProps) {
  const { deleteVendor, isLoading } = useDeleteVendor();

  async function handleDelete() {
    try {
      await deleteVendor(vendorId);
      toast.success(`${vendorName} deleted`);
      onOpenChange(false);
      onDeleted();
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "Failed to delete vendor"
      );
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-1">
            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-risk-critical/10">
              <AlertTriangle className="h-5 w-5 text-risk-critical" />
            </div>
            <DialogTitle>Delete Vendor</DialogTitle>
          </div>
          <DialogDescription>
            Are you sure you want to delete <strong>{vendorName}</strong>? This
            action cannot be undone. All associated data including contacts,
            assessments, and documents will be permanently removed.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={handleDelete} disabled={isLoading}>
            {isLoading ? "Deleting..." : "Delete Vendor"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
