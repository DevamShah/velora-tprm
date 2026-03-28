"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { VendorForm } from "@/components/vendors/vendor-form";
import { useCreateVendor } from "@/hooks/use-vendors";
import type { CreateVendorPayload } from "@/types/vendor";

export default function NewVendorPage() {
  const router = useRouter();
  const { createVendor, isLoading } = useCreateVendor();

  async function handleSubmit(data: CreateVendorPayload) {
    try {
      const vendor = await createVendor(data);
      toast.success("Vendor created successfully");
      router.push(`/vendors/${vendor.id}`);
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "Failed to create vendor"
      );
    }
  }

  return (
    <>
      <PageHeader
        title="Add Vendor"
        description="Register a new third-party vendor"
        actions={
          <Button variant="ghost" onClick={() => router.push("/vendors")}>
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Vendors
          </Button>
        }
      />
      <VendorForm
        onSubmit={handleSubmit}
        onCancel={() => router.push("/vendors")}
        isLoading={isLoading}
        submitLabel="Create Vendor"
      />
    </>
  );
}
