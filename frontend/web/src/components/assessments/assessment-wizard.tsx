"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Building2,
  ClipboardCheck,
  FileText,
  ChevronRight,
  ChevronLeft,
  Check,
  Search,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useCreateAssessment, useAssessmentTemplates } from "@/hooks/use-assessments";
import { api } from "@/lib/api";
import type { Vendor, VendorListResponse } from "@/types/vendor";
import type { AssessmentTemplate, CreateAssessmentPayload } from "@/types/assessment";

const STEPS = [
  { label: "Select Vendor", icon: Building2 },
  { label: "Select Template", icon: ClipboardCheck },
  { label: "Assessment Details", icon: FileText },
];

export function AssessmentWizard() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<AssessmentTemplate | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState("");
  const { createAssessment, isLoading: creating } = useCreateAssessment();

  function canProceed(): boolean {
    switch (step) {
      case 0:
        return !!selectedVendor;
      case 1:
        return !!selectedTemplate;
      case 2:
        return !!title.trim();
      default:
        return false;
    }
  }

  async function handleSubmit() {
    if (!selectedVendor || !selectedTemplate || !title.trim()) return;

    const payload: CreateAssessmentPayload = {
      vendor_id: selectedVendor.id,
      template_id: selectedTemplate.id,
      title: title.trim(),
      description: description.trim() || undefined,
      due_date: dueDate || undefined,
    };

    try {
      const assessment = await createAssessment(payload);
      toast.success("Assessment created successfully");
      router.push(`/assessments/${assessment.id}`);
    } catch (err) {
      toast.error((err as { message?: string }).message || "Failed to create assessment");
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Step indicator */}
      <div className="flex items-center justify-between">
        {STEPS.map((s, i) => {
          const Icon = s.icon;
          const isActive = i === step;
          const isCompleted = i < step;
          return (
            <React.Fragment key={s.label}>
              <div className="flex items-center gap-3">
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 ${
                    isCompleted
                      ? "bg-emerald-100 text-emerald-700"
                      : isActive
                      ? "bg-accent-primary/10 text-accent-primary"
                      : "bg-surface-main text-text-muted"
                  }`}
                >
                  {isCompleted ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </div>
                <div>
                  <p className="text-xs text-text-muted">Step {i + 1}</p>
                  <p
                    className={`text-sm font-medium ${
                      isActive ? "text-text-primary" : "text-text-muted"
                    }`}
                  >
                    {s.label}
                  </p>
                </div>
              </div>
              {i < STEPS.length - 1 && (
                <div
                  className={`flex-1 h-px mx-4 ${
                    i < step ? "bg-emerald-300" : "bg-surface-card-border"
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Step content */}
      <div className="animate-fade-in">
        {step === 0 && (
          <VendorSelector
            selected={selectedVendor}
            onSelect={setSelectedVendor}
          />
        )}
        {step === 1 && (
          <TemplateSelector
            selected={selectedTemplate}
            onSelect={setSelectedTemplate}
          />
        )}
        {step === 2 && (
          <DetailsForm
            vendor={selectedVendor!}
            template={selectedTemplate!}
            title={title}
            description={description}
            dueDate={dueDate}
            onTitleChange={setTitle}
            onDescriptionChange={setDescription}
            onDueDateChange={setDueDate}
          />
        )}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-4 border-t border-surface-card-border">
        <Button
          variant="outline"
          onClick={() => (step === 0 ? router.push("/assessments") : setStep(step - 1))}
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          {step === 0 ? "Cancel" : "Back"}
        </Button>
        {step < 2 ? (
          <Button onClick={() => setStep(step + 1)} disabled={!canProceed()}>
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        ) : (
          <Button onClick={handleSubmit} disabled={!canProceed() || creating}>
            {creating ? (
              <Loader2 className="h-4 w-4 mr-1 animate-spin" />
            ) : (
              <Check className="h-4 w-4 mr-1" />
            )}
            {creating ? "Creating..." : "Create Assessment"}
          </Button>
        )}
      </div>
    </div>
  );
}

/* --- Step 1: Vendor Selector --- */

function VendorSelector({
  selected,
  onSelect,
}: {
  selected: Vendor | null;
  onSelect: (v: Vendor) => void;
}) {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState("");

  const fetchVendors = useCallback(async (q: string) => {
    setIsLoading(true);
    try {
      const params: Record<string, string> = { page_size: "50" };
      if (q) params.search = q;
      const res = await api.get<VendorListResponse>("/vendors", params);
      setVendors(res.items);
    } catch {
      toast.error("Failed to load vendors");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => fetchVendors(search), 300);
    return () => clearTimeout(timer);
  }, [search, fetchVendors]);

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-text-primary">Select a Vendor</h2>
        <p className="text-sm text-text-muted mt-1">
          Choose the vendor you want to assess.
        </p>
      </div>
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
        <Input
          placeholder="Search vendors..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 bg-surface-main animate-pulse rounded-xl" />
          ))}
        </div>
      ) : vendors.length === 0 ? (
        <div className="text-center py-8 text-sm text-text-muted">
          No vendors found. Try a different search.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[400px] overflow-y-auto pr-1">
          {vendors.map((vendor) => {
            const isSelected = selected?.id === vendor.id;
            return (
              <button
                key={vendor.id}
                onClick={() => onSelect(vendor)}
                className={`text-left p-4 rounded-xl border-2 transition-all duration-150 ${
                  isSelected
                    ? "border-accent-primary bg-accent-primary/5"
                    : "border-surface-card-border bg-white hover:border-accent-primary/40"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-text-primary">
                      {vendor.name}
                    </p>
                    {vendor.domain && (
                      <p className="text-xs text-text-muted mt-0.5">
                        {vendor.domain}
                      </p>
                    )}
                  </div>
                  {isSelected && (
                    <div className="w-5 h-5 rounded-full bg-accent-primary flex items-center justify-center">
                      <Check className="h-3 w-3 text-white" />
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-2">
                  {vendor.tier && vendor.tier !== "unclassified" && (
                    <Badge variant="outline" className="text-[10px]">
                      {vendor.tier}
                    </Badge>
                  )}
                  {vendor.industry && (
                    <span className="text-xs text-text-muted">{vendor.industry}</span>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* --- Step 2: Template Selector --- */

function TemplateSelector({
  selected,
  onSelect,
}: {
  selected: AssessmentTemplate | null;
  onSelect: (t: AssessmentTemplate) => void;
}) {
  const { templates, isLoading, error } = useAssessmentTemplates();

  if (error) {
    return (
      <div className="text-center py-8 text-sm text-red-600">
        Failed to load templates: {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-text-primary">Select a Template</h2>
        <p className="text-sm text-text-muted mt-1">
          Choose the assessment template to use for this evaluation.
        </p>
      </div>
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-32 bg-surface-main animate-pulse rounded-xl" />
          ))}
        </div>
      ) : templates.length === 0 ? (
        <div className="text-center py-8 text-sm text-text-muted">
          No templates available. Create a template first.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {templates.map((template) => {
            const isSelected = selected?.id === template.id;
            return (
              <button
                key={template.id}
                onClick={() => onSelect(template)}
                className={`text-left p-4 rounded-xl border-2 transition-all duration-150 ${
                  isSelected
                    ? "border-accent-primary bg-accent-primary/5"
                    : "border-surface-card-border bg-white hover:border-accent-primary/40"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-text-primary">
                      {template.name}
                    </p>
                    {template.description && (
                      <p className="text-xs text-text-muted mt-1 line-clamp-2">
                        {template.description}
                      </p>
                    )}
                  </div>
                  {isSelected && (
                    <div className="w-5 h-5 rounded-full bg-accent-primary flex items-center justify-center ml-2 shrink-0">
                      <Check className="h-3 w-3 text-white" />
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-surface-card-border">
                  <ClipboardCheck className="h-3.5 w-3.5 text-text-muted" />
                  <span className="text-xs text-text-muted">
                    {template.question_count} question{template.question_count !== 1 ? "s" : ""}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* --- Step 3: Details Form --- */

function DetailsForm({
  vendor,
  template,
  title,
  description,
  dueDate,
  onTitleChange,
  onDescriptionChange,
  onDueDateChange,
}: {
  vendor: Vendor;
  template: AssessmentTemplate;
  title: string;
  description: string;
  dueDate: string;
  onTitleChange: (v: string) => void;
  onDescriptionChange: (v: string) => void;
  onDueDateChange: (v: string) => void;
}) {
  // Auto-populate title on first render if empty
  useEffect(() => {
    if (!title) {
      onTitleChange(`${template.name} - ${vendor.name}`);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary">Assessment Details</h2>
        <p className="text-sm text-text-muted mt-1">
          Configure the details for this assessment.
        </p>
      </div>

      {/* Summary of selections */}
      <div className="flex gap-3">
        <Card className="flex-1">
          <CardContent className="pt-4 pb-4">
            <p className="text-xs text-text-muted mb-1">Vendor</p>
            <p className="text-sm font-medium text-text-primary">{vendor.name}</p>
            {vendor.domain && (
              <p className="text-xs text-text-muted">{vendor.domain}</p>
            )}
          </CardContent>
        </Card>
        <Card className="flex-1">
          <CardContent className="pt-4 pb-4">
            <p className="text-xs text-text-muted mb-1">Template</p>
            <p className="text-sm font-medium text-text-primary">{template.name}</p>
            <p className="text-xs text-text-muted">
              {template.question_count} questions
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Form fields */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-text-primary mb-1.5">
            Assessment Title <span className="text-red-500">*</span>
          </label>
          <Input
            value={title}
            onChange={(e) => onTitleChange(e.target.value)}
            placeholder="Enter assessment title..."
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-text-primary mb-1.5">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => onDescriptionChange(e.target.value)}
            placeholder="Optional description..."
            rows={3}
            className="w-full px-3 py-2 text-sm rounded-lg border border-surface-card-border bg-white text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary resize-y"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-text-primary mb-1.5">
            Due Date
          </label>
          <Input
            type="date"
            value={dueDate}
            onChange={(e) => onDueDateChange(e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}
