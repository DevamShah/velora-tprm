"use client";

import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import {
  VENDOR_STATUSES,
  VENDOR_TIERS,
  DATA_CLASSIFICATIONS,
  BUSINESS_CRITICALITIES,
} from "@/types/vendor";
import type { CreateVendorPayload } from "@/types/vendor";

interface VendorFormProps {
  initialData?: Partial<CreateVendorPayload>;
  onSubmit: (data: CreateVendorPayload) => void;
  onCancel: () => void;
  isLoading: boolean;
  submitLabel: string;
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function FieldLabel({ children, required }: { children: React.ReactNode; required?: boolean }) {
  return (
    <label className="text-sm font-medium text-text-primary block mb-1.5">
      {children}
      {required && <span className="text-risk-critical ml-0.5">*</span>}
    </label>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-sm font-semibold text-text-primary mb-3 pb-2 border-b border-surface-card-border">
      {children}
    </h3>
  );
}

export function VendorForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading,
  submitLabel,
}: VendorFormProps) {
  const [name, setName] = useState(initialData?.name || "");
  const [domain, setDomain] = useState(initialData?.domain || "");
  const [industry, setIndustry] = useState(initialData?.industry || "");
  const [country, setCountry] = useState(initialData?.country || "");
  const [description, setDescription] = useState(initialData?.description || "");
  const [status, setStatus] = useState(initialData?.status || "");
  const [tier, setTier] = useState(initialData?.tier || "");
  const [dataClass, setDataClass] = useState(initialData?.data_classification || "");
  const [bizCrit, setBizCrit] = useState(initialData?.business_criticality || "");
  const [contractValue, setContractValue] = useState(
    initialData?.contract_value?.toString() || ""
  );
  const [contractStart, setContractStart] = useState(initialData?.contract_start_date || "");
  const [contractEnd, setContractEnd] = useState(initialData?.contract_end_date || "");
  const [tagsStr, setTagsStr] = useState(initialData?.tags?.join(", ") || "");
  const [notes, setNotes] = useState(initialData?.notes || "");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const data: CreateVendorPayload = { name };
    if (domain) data.domain = domain;
    if (description) data.description = description;
    if (industry) data.industry = industry;
    if (country) data.country = country;
    if (status) data.status = status as CreateVendorPayload["status"];
    if (tier) data.tier = tier as CreateVendorPayload["tier"];
    if (dataClass) data.data_classification = dataClass as CreateVendorPayload["data_classification"];
    if (bizCrit) data.business_criticality = bizCrit as CreateVendorPayload["business_criticality"];
    if (contractValue) data.contract_value = Number(contractValue);
    if (contractStart) data.contract_start_date = contractStart;
    if (contractEnd) data.contract_end_date = contractEnd;
    if (tagsStr.trim()) {
      data.tags = tagsStr.split(",").map((t) => t.trim()).filter(Boolean);
    }
    if (notes) data.notes = notes;
    onSubmit(data);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardContent className="pt-6 space-y-4">
          <SectionTitle>Basic Information</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <FieldLabel required>Name</FieldLabel>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Amazon Web Services"
                required
              />
            </div>
            <div>
              <FieldLabel>Domain</FieldLabel>
              <Input
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="e.g. aws.amazon.com"
              />
            </div>
            <div>
              <FieldLabel>Industry</FieldLabel>
              <Input
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="e.g. Cloud Computing"
              />
            </div>
            <div>
              <FieldLabel>Country</FieldLabel>
              <Input
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                placeholder="e.g. United States"
              />
            </div>
          </div>
          <div>
            <FieldLabel>Description</FieldLabel>
            <textarea
              className="w-full h-20 rounded-lg border border-surface-card-border bg-white px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary transition-all resize-none"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the vendor..."
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6 space-y-4">
          <SectionTitle>Classification</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <FieldLabel>Status</FieldLabel>
              <Select value={status || "none"} onValueChange={(v) => setStatus(v === "none" ? "" : v)}>
                <SelectTrigger><SelectValue placeholder="Select status" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Select status</SelectItem>
                  {VENDOR_STATUSES.map((s) => (
                    <SelectItem key={s} value={s}>{capitalize(s)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <FieldLabel>Tier</FieldLabel>
              <Select value={tier || "none"} onValueChange={(v) => setTier(v === "none" ? "" : v)}>
                <SelectTrigger><SelectValue placeholder="Select tier" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Select tier</SelectItem>
                  {VENDOR_TIERS.map((t) => (
                    <SelectItem key={t} value={t}>{capitalize(t)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <FieldLabel>Data Classification</FieldLabel>
              <Select value={dataClass || "none"} onValueChange={(v) => setDataClass(v === "none" ? "" : v)}>
                <SelectTrigger><SelectValue placeholder="Select classification" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Select classification</SelectItem>
                  {DATA_CLASSIFICATIONS.map((d) => (
                    <SelectItem key={d} value={d}>{capitalize(d)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <FieldLabel>Business Criticality</FieldLabel>
              <Select value={bizCrit || "none"} onValueChange={(v) => setBizCrit(v === "none" ? "" : v)}>
                <SelectTrigger><SelectValue placeholder="Select criticality" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Select criticality</SelectItem>
                  {BUSINESS_CRITICALITIES.map((b) => (
                    <SelectItem key={b} value={b}>{capitalize(b)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6 space-y-4">
          <SectionTitle>Contract Details</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <FieldLabel>Contract Value ($)</FieldLabel>
              <Input
                type="number"
                value={contractValue}
                onChange={(e) => setContractValue(e.target.value)}
                placeholder="e.g. 50000"
                min="0"
              />
            </div>
            <div>
              <FieldLabel>Start Date</FieldLabel>
              <Input
                type="date"
                value={contractStart}
                onChange={(e) => setContractStart(e.target.value)}
              />
            </div>
            <div>
              <FieldLabel>End Date</FieldLabel>
              <Input
                type="date"
                value={contractEnd}
                onChange={(e) => setContractEnd(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6 space-y-4">
          <SectionTitle>Additional</SectionTitle>
          <div>
            <FieldLabel>Tags (comma-separated)</FieldLabel>
            <Input
              value={tagsStr}
              onChange={(e) => setTagsStr(e.target.value)}
              placeholder="e.g. cloud, infrastructure, critical"
            />
          </div>
          <div>
            <FieldLabel>Notes</FieldLabel>
            <textarea
              className="w-full h-24 rounded-lg border border-surface-card-border bg-white px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary transition-all resize-none"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any additional notes..."
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center justify-end gap-3">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading || !name.trim()}>
          {isLoading ? "Saving..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}
