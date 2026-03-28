// Communication domain types — maps 1:1 to backend API schema

export type NotificationType =
  | "alert"
  | "assessment"
  | "finding"
  | "vendor"
  | "system"
  | "reminder";

export type NotificationPriority = "high" | "medium" | "low";

export interface Notification {
  id: string;
  tenant_id: string;
  user_id: string;
  type: NotificationType;
  priority: NotificationPriority;
  title: string;
  message: string;
  link: string | null;
  is_read: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  unread_count: number;
}

export interface NotificationPreferences {
  email_enabled: boolean;
  in_app_enabled: boolean;
  alert_notifications: boolean;
  assessment_notifications: boolean;
  finding_notifications: boolean;
  vendor_notifications: boolean;
  system_notifications: boolean;
  digest_frequency: "realtime" | "hourly" | "daily" | "weekly";
}

export interface EmailTemplate {
  id: string;
  tenant_id: string;
  name: string;
  subject: string;
  body_template: string;
  variables: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CommunicationLog {
  id: string;
  tenant_id: string;
  channel: "email" | "in_app" | "webhook" | "slack";
  recipient: string;
  subject: string | null;
  status: "sent" | "delivered" | "failed" | "pending";
  sent_at: string;
  error_message: string | null;
}

export interface CommunicationLogListResponse {
  items: CommunicationLog[];
  total: number;
  page: number;
  page_size: number;
}

export const NOTIFICATION_TYPE_LABELS: Record<NotificationType, string> = {
  alert: "Alert",
  assessment: "Assessment",
  finding: "Finding",
  vendor: "Vendor",
  system: "System",
  reminder: "Reminder",
};

export const NOTIFICATION_PRIORITY_LABELS: Record<NotificationPriority, string> = {
  high: "High",
  medium: "Medium",
  low: "Low",
};

export const COMM_CHANNEL_LABELS: Record<string, string> = {
  email: "Email",
  in_app: "In-App",
  webhook: "Webhook",
  slack: "Slack",
};

export const COMM_STATUS_LABELS: Record<string, string> = {
  sent: "Sent",
  delivered: "Delivered",
  failed: "Failed",
  pending: "Pending",
};
