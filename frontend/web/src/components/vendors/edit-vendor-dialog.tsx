"use client";

import React from "react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { VendorForm } from "@/components/vendors/vendor-form";
import { useUpdateVendor } from "@/hooks/use-vendors";
import type { VendorDetail, CreateVendorPayload } from "@/types/vendor";

interface EditVendorDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  vendor: VendorDetail;
  onSuccess: () => void;
}

export function EditVendorDialog({
  open,
  onOpenChange,
  vendor,
  onSuccess,
}: EditVendorDialogProps) {
  const { updateVendor, isLoading } = useUpdateVendor();

  async function handleSubmit(data: CreateVendorPayload) {
    try {
      await updateVendor(vendor.id, data);
      toast.success("Vendor updated");
      onOpenChange(false);
      onSuccess();
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "Failed to update vendor"
      );
    }
  }

  const initialData: Partial<CreateVendorPayload> = {
    name: vendor.name,
    domain: vendor.domain || undefined,
    description: vendor.description || undefined,
    industry: vendor.industry || undefined,
    country: vendor.country || undefined,
    status: vendor.status,
    tier: vendor.tier,
    data_classification: vendor.data_classification || undefined,
    business_criticality: vendor.business_criticality || undefined,
    contract_value: vendor.contract_value || undefined,
    contract_start_date: vendor.contract_start_date || undefined,
    contract_end_date: vendor.contract_end_date || undefined,
    tags: vendor.tags,
    notes: vendor.notes || undefined,
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Vendor</DialogTitle>
          <DialogDescription>
            Update the details for {vendor.name}.
          </DialogDescription>
        </DialogHeader>
        <VendorForm
          initialData={initialData}
          onSubmit={handleSubmit}
          onCancel={() => onOpenChange(false)}
          isLoading={isLoading}
          submitLabel="Save Changes"
        />
      </DialogContent>
    </Dialog>
  );
}
