// Monitoring domain types — maps 1:1 to backend API schema

export type AlertPriority = "p0" | "p1" | "p2" | "p3" | "p4";

export type AlertStatus =
  | "new"
  | "acknowledged"
  | "investigating"
  | "resolved"
  | "suppressed";

export type AlertSource =
  | "breach_feed"
  | "dark_web"
  | "regulatory"
  | "certificate"
  | "reputation"
  | "financial"
  | "compliance"
  | "manual";

export type TimelineEventType =
  | "alert"
  | "assessment"
  | "evidence"
  | "status_change"
  | "score_change"
  | "communication"
  | "note";

export interface Alert {
  id: string;
  tenant_id: string;
  vendor_id: string;
  vendor_name: string;
  title: string;
  description: string | null;
  priority: AlertPriority;
  status: AlertStatus;
  source: AlertSource;
  impact_assessment: string | null;
  recommended_actions: string[] | null;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  resolved_by: string | null;
  resolved_at: string | null;
  resolution_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertDetail extends Alert {
  raw_data: Record<string, unknown> | null;
  related_alerts: Array<{
    id: string;
    title: string;
    priority: AlertPriority;
    status: AlertStatus;
  }>;
}

export interface AlertListResponse {
  items: Alert[];
  total: number;
  page: number;
  page_size: number;
}

export interface AlertFilters {
  priority?: AlertPriority | "";
  status?: AlertStatus | "";
  source?: AlertSource | "";
  vendor_id?: string;
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface TimelineEvent {
  id: string;
  vendor_id: string;
  event_type: TimelineEventType;
  title: string;
  description: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
  created_by: string | null;
}

export interface AlertRule {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  enabled: boolean;
  conditions: AlertRuleCondition[];
  actions: AlertRuleAction[];
  created_at: string;
  updated_at: string;
}

export interface AlertRuleCondition {
  field: string;
  operator: "eq" | "ne" | "gt" | "lt" | "gte" | "lte" | "contains";
  value: string;
}

export interface AlertRuleAction {
  type: "create_alert" | "send_notification" | "escalate";
  priority?: AlertPriority;
  notify_emails?: string[];
}

export interface CreateAlertRulePayload {
  name: string;
  description?: string;
  enabled?: boolean;
  conditions: AlertRuleCondition[];
  actions: AlertRuleAction[];
}

export const ALERT_PRIORITIES: AlertPriority[] = ["p0", "p1", "p2", "p3", "p4"];

export const ALERT_STATUSES: AlertStatus[] = [
  "new",
  "acknowledged",
  "investigating",
  "resolved",
  "suppressed",
];

export const ALERT_SOURCES: AlertSource[] = [
  "breach_feed",
  "dark_web",
  "regulatory",
  "certificate",
  "reputation",
  "financial",
  "compliance",
  "manual",
];

export const ALERT_PRIORITY_LABELS: Record<AlertPriority, string> = {
  p0: "P0 - Critical",
  p1: "P1 - High",
  p2: "P2 - Medium",
  p3: "P3 - Low",
  p4: "P4 - Info",
};

export const ALERT_STATUS_LABELS: Record<AlertStatus, string> = {
  new: "New",
  acknowledged: "Acknowledged",
  investigating: "Investigating",
  resolved: "Resolved",
  suppressed: "Suppressed",
};

export const ALERT_SOURCE_LABELS: Record<AlertSource, string> = {
  breach_feed: "Breach Feed",
  dark_web: "Dark Web",
  regulatory: "Regulatory",
  certificate: "Certificate",
  reputation: "Reputation",
  financial: "Financial",
  compliance: "Compliance",
  manual: "Manual",
};

export const TIMELINE_EVENT_TYPE_LABELS: Record<TimelineEventType, string> = {
  alert: "Alert",
  assessment: "Assessment",
  evidence: "Evidence",
  status_change: "Status Change",
  score_change: "Score Change",
  communication: "Communication",
  note: "Note",
};
