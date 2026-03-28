// Finding domain types — maps 1:1 to backend API schema

export type FindingSeverity = "critical" | "high" | "medium" | "low" | "info";

export type FindingStatus =
  | "open"
  | "in_progress"
  | "remediated"
  | "accepted"
  | "closed"
  | "false_positive";

export type RemediationStatus =
  | "planned"
  | "in_progress"
  | "completed"
  | "verified"
  | "overdue";

export interface Finding {
  id: string;
  tenant_id: string;
  vendor_id: string;
  vendor_name: string;
  assessment_id: string | null;
  title: string;
  description: string | null;
  severity: FindingSeverity;
  status: FindingStatus;
  affected_controls: string[];
  sla_due_date: string | null;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
}

export interface RemediationAction {
  id: string;
  finding_id: string;
  title: string;
  description: string | null;
  status: RemediationStatus;
  assigned_to: string | null;
  due_date: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface FindingDetail extends Finding {
  remediation_guidance: string | null;
  remediation_actions: RemediationAction[];
  evidence_ids: string[];
}

export interface FindingListResponse {
  items: Finding[];
  total: number;
  page: number;
  page_size: number;
}

export interface FindingFilters {
  severity?: FindingSeverity | "";
  status?: FindingStatus | "";
  vendor_id?: string;
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface CreateFindingPayload {
  vendor_id: string;
  assessment_id?: string;
  title: string;
  description?: string;
  severity: FindingSeverity;
  affected_controls?: string[];
  sla_due_date?: string;
  assigned_to?: string;
  remediation_guidance?: string;
}

export interface CreateRemediationPayload {
  title: string;
  description?: string;
  assigned_to?: string;
  due_date?: string;
}

export interface UpdateRemediationPayload {
  status?: RemediationStatus;
  title?: string;
  description?: string;
  assigned_to?: string;
  due_date?: string;
}

export const FINDING_SEVERITIES: FindingSeverity[] = [
  "critical",
  "high",
  "medium",
  "low",
  "info",
];

export const FINDING_STATUSES: FindingStatus[] = [
  "open",
  "in_progress",
  "remediated",
  "accepted",
  "closed",
  "false_positive",
];

export const FINDING_SEVERITY_LABELS: Record<FindingSeverity, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  info: "Info",
};

export const FINDING_STATUS_LABELS: Record<FindingStatus, string> = {
  open: "Open",
  in_progress: "In Progress",
  remediated: "Remediated",
  accepted: "Accepted",
  closed: "Closed",
  false_positive: "False Positive",
};

export const REMEDIATION_STATUS_LABELS: Record<RemediationStatus, string> = {
  planned: "Planned",
  in_progress: "In Progress",
  completed: "Completed",
  verified: "Verified",
  overdue: "Overdue",
};
