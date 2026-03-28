// Dashboard domain types — maps 1:1 to backend API schema

export interface DashboardData {
  total_vendors: number;
  vendors_by_tier: Record<string, number>;
  total_assessments: number;
  assessments_by_status: Record<string, number>;
  open_findings: number;
  findings_by_severity: Record<string, number>;
  active_alerts: number;
  alerts_by_priority: Record<string, number>;
  avg_risk_score: number;
  recent_alerts: DashboardAlert[];
  top_risk_vendors: DashboardVendor[];
}

export interface DashboardAlert {
  id: string;
  title: string;
  priority: string;
  vendor_name: string;
  created_at: string;
}

export interface DashboardVendor {
  id: string;
  name: string;
  tier: string;
  risk_score: number;
  trend: "up" | "down" | "stable";
}

export interface Report {
  id: string;
  tenant_id: string;
  name: string;
  template: string;
  format: "pdf" | "csv";
  status: ReportStatus;
  generated_by: string | null;
  file_url: string | null;
  created_at: string;
  completed_at: string | null;
}

export type ReportStatus = "pending" | "generating" | "completed" | "failed";

export interface ReportListResponse {
  items: Report[];
  total: number;
  page: number;
  page_size: number;
}

export interface GenerateReportPayload {
  template: string;
  format: "pdf" | "csv";
  name?: string;
}

export const REPORT_TEMPLATES = [
  { value: "executive_summary", label: "Executive Summary" },
  { value: "vendor_risk_report", label: "Vendor Risk Report" },
  { value: "compliance_status", label: "Compliance Status" },
  { value: "assessment_summary", label: "Assessment Summary" },
  { value: "findings_report", label: "Findings Report" },
  { value: "trend_analysis", label: "Trend Analysis" },
] as const;

export const REPORT_STATUS_LABELS: Record<ReportStatus, string> = {
  pending: "Pending",
  generating: "Generating",
  completed: "Completed",
  failed: "Failed",
};
