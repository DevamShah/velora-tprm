"use client";

import React, { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { useCreateContact } from "@/hooks/use-vendors";
import type { VendorContact, CreateContactPayload } from "@/types/vendor";

interface AddContactDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  vendorId: string;
  onSuccess: () => void;
  editData?: VendorContact | null;
  onEdit?: (contactId: string, data: Partial<CreateContactPayload>) => Promise<void>;
}

function FieldLabel({ children, required }: { children: React.ReactNode; required?: boolean }) {
  return (
    <label className="text-sm font-medium text-text-primary block mb-1.5">
      {children}
      {required && <span className="text-risk-critical ml-0.5">*</span>}
    </label>
  );
}

export function AddContactDialog({
  open,
  onOpenChange,
  vendorId,
  onSuccess,
  editData,
  onEdit,
}: AddContactDialogProps) {
  const [firstName, setFirstName] = useState(editData?.first_name || "");
  const [lastName, setLastName] = useState(editData?.last_name || "");
  const [email, setEmail] = useState(editData?.email || "");
  const [phone, setPhone] = useState(editData?.phone || "");
  const [role, setRole] = useState(editData?.role || "");
  const [isPrimary, setIsPrimary] = useState(editData?.is_primary || false);
  const { createContact, isLoading: creating } = useCreateContact();
  const [editLoading, setEditLoading] = useState(false);

  const isEdit = !!editData;
  const isLoading = creating || editLoading;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const data: CreateContactPayload = {
      first_name: firstName,
      last_name: lastName,
      email,
    };
    if (phone) data.phone = phone;
    if (role) data.role = role;
    data.is_primary = isPrimary;

    try {
      if (isEdit && onEdit && editData) {
        setEditLoading(true);
        await onEdit(editData.id, data);
        setEditLoading(false);
        toast.success("Contact updated");
      } else {
        await createContact(vendorId, data);
        toast.success("Contact added");
      }
      onSuccess();
      handleClose(false);
    } catch (err) {
      setEditLoading(false);
      toast.error((err as { message?: string }).message || "Failed to save contact");
    }
  }

  function handleClose(val: boolean) {
    if (!val) {
      setFirstName("");
      setLastName("");
      setEmail("");
      setPhone("");
      setRole("");
      setIsPrimary(false);
    }
    onOpenChange(val);
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit Contact" : "Add Contact"}</DialogTitle>
          <DialogDescription>
            {isEdit
              ? "Update the contact details."
              : "Add a new contact for this vendor."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel required>First Name</FieldLabel>
              <Input
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                placeholder="John"
                required
              />
            </div>
            <div>
              <FieldLabel required>Last Name</FieldLabel>
              <Input
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                placeholder="Smith"
                required
              />
            </div>
          </div>
          <div>
            <FieldLabel required>Email</FieldLabel>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="john@company.com"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel>Phone</FieldLabel>
              <Input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 000-0000"
              />
            </div>
            <div>
              <FieldLabel>Role</FieldLabel>
              <Input
                value={role}
                onChange={(e) => setRole(e.target.value)}
                placeholder="e.g. Account Manager"
              />
            </div>
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isPrimary}
              onChange={(e) => setIsPrimary(e.target.checked)}
              className="rounded border-surface-card-border text-accent-primary focus:ring-accent-primary"
            />
            <span className="text-sm text-text-primary">Primary contact</span>
          </label>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => handleClose(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading || !firstName.trim() || !lastName.trim() || !email.trim()}
            >
              {isLoading ? "Saving..." : isEdit ? "Update" : "Add Contact"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
