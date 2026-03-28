"use client";

import React from "react";
import { CheckCircle2, XCircle, FileUp, Calendar, Hash } from "lucide-react";
import type { AssessmentQuestion } from "@/types/assessment";

interface QuestionRendererProps {
  question: AssessmentQuestion;
  value: string | null;
  readOnly?: boolean;
}

export function QuestionRenderer({ question, value, readOnly = true }: QuestionRendererProps) {
  switch (question.question_type) {
    case "yes_no":
      return <YesNoDisplay value={value} />;
    case "multiple_choice":
      return <MultipleChoiceDisplay value={value} options={question.options} />;
    case "text":
      return <TextDisplay value={value} />;
    case "file_upload":
      return <FileUploadDisplay value={value} />;
    case "scale":
      return <ScaleDisplay value={value} />;
    case "date":
      return <DateDisplay value={value} />;
    default:
      return <TextDisplay value={value} />;
  }
}

function YesNoDisplay({ value }: { value: string | null }) {
  if (!value) return <span className="text-sm text-text-muted italic">No response</span>;
  const isYes = value.toLowerCase() === "yes" || value === "true";
  return (
    <div className="flex items-center gap-2">
      {isYes ? (
        <CheckCircle2 className="h-5 w-5 text-emerald-600" />
      ) : (
        <XCircle className="h-5 w-5 text-red-500" />
      )}
      <span className="text-sm font-medium text-text-primary">
        {isYes ? "Yes" : "No"}
      </span>
    </div>
  );
}

function MultipleChoiceDisplay({
  value,
  options,
}: {
  value: string | null;
  options: string[] | null;
}) {
  if (!value) return <span className="text-sm text-text-muted italic">No response</span>;
  return (
    <div className="space-y-1.5">
      {(options || []).map((opt) => {
        const isSelected = value === opt;
        return (
          <div
            key={opt}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm ${
              isSelected
                ? "bg-accent-primary/10 text-accent-primary font-medium"
                : "bg-surface-main text-text-muted"
            }`}
          >
            <div
              className={`w-3.5 h-3.5 rounded-full border-2 flex items-center justify-center ${
                isSelected ? "border-accent-primary" : "border-surface-card-border"
              }`}
            >
              {isSelected && (
                <div className="w-1.5 h-1.5 rounded-full bg-accent-primary" />
              )}
            </div>
            {opt}
          </div>
        );
      })}
    </div>
  );
}

function TextDisplay({ value }: { value: string | null }) {
  if (!value) return <span className="text-sm text-text-muted italic">No response</span>;
  return (
    <div className="px-3 py-2 rounded-lg bg-surface-main text-sm text-text-primary whitespace-pre-wrap">
      {value}
    </div>
  );
}

function FileUploadDisplay({ value }: { value: string | null }) {
  if (!value) return <span className="text-sm text-text-muted italic">No file uploaded</span>;
  return (
    <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-main">
      <FileUp className="h-4 w-4 text-text-muted" />
      <span className="text-sm text-accent-primary underline">{value}</span>
    </div>
  );
}

function ScaleDisplay({ value }: { value: string | null }) {
  if (!value) return <span className="text-sm text-text-muted italic">No response</span>;
  const num = parseInt(value, 10);
  const maxScale = 10;
  return (
    <div className="flex items-center gap-3">
      <Hash className="h-4 w-4 text-text-muted" />
      <div className="flex items-center gap-1">
        {Array.from({ length: maxScale }).map((_, i) => (
          <div
            key={i}
            className={`w-6 h-6 rounded flex items-center justify-center text-xs font-medium ${
              i < num
                ? "bg-accent-primary text-white"
                : "bg-surface-main text-text-muted"
            }`}
          >
            {i + 1}
          </div>
        ))}
      </div>
      <span className="text-sm font-medium text-text-primary">{num}/10</span>
    </div>
  );
}

function DateDisplay({ value }: { value: string | null }) {
  if (!value) return <span className="text-sm text-text-muted italic">No response</span>;
  const formatted = new Date(value).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
  return (
    <div className="flex items-center gap-2">
      <Calendar className="h-4 w-4 text-text-muted" />
      <span className="text-sm text-text-primary">{formatted}</span>
    </div>
  );
}
