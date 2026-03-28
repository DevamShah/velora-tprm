import { Badge } from "@/components/ui/badge";
import type { AssessmentStatus } from "@/types/assessment";

const STATUS_STYLES: Record<AssessmentStatus, string> = {
  draft: "bg-slate-100 text-slate-600",
  distributed: "bg-blue-50 text-blue-700",
  in_progress: "bg-amber-50 text-amber-700",
  submitted: "bg-purple-50 text-purple-700",
  under_review: "bg-orange-50 text-orange-700",
  completed: "bg-emerald-50 text-emerald-700",
  cancelled: "bg-red-50 text-red-700",
};

const STATUS_LABEL: Record<AssessmentStatus, string> = {
  draft: "Draft",
  distributed: "Distributed",
  in_progress: "In Progress",
  submitted: "Submitted",
  under_review: "Under Review",
  completed: "Completed",
  cancelled: "Cancelled",
};

interface AssessmentStatusBadgeProps {
  status: AssessmentStatus;
  className?: string;
}

export function AssessmentStatusBadge({ status, className }: AssessmentStatusBadgeProps) {
  return (
    <Badge variant="outline" className={`${STATUS_STYLES[status]} border-0 ${className || ""}`}>
      {STATUS_LABEL[status]}
    </Badge>
  );
}

export { STATUS_LABEL };
