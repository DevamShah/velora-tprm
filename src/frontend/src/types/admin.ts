// Admin domain types — maps 1:1 to backend API schema

export type UserStatus = "active" | "inactive" | "invited" | "suspended";

export interface AdminUser {
  id: string;
  tenant_id: string;
  email: string;
  name: string;
  status: UserStatus;
  roles: string[];
  last_login: string | null;
  created_at: string;
  updated_at: string;
}

export interface AdminUserListResponse {
  items: AdminUser[];
  total: number;
  page: number;
  page_size: number;
}

export interface CreateUserPayload {
  email: string;
  name: string;
  roles?: string[];
}

export interface UpdateUserPayload {
  name?: string;
  email?: string;
  status?: UserStatus;
}

export interface AssignRolesPayload {
  roles: string[];
}

export interface Role {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  permissions: string[];
  is_system: boolean;
  user_count: number;
  created_at: string;
}

export interface CreateRolePayload {
  name: string;
  description?: string;
  permissions: string[];
}

export type AuditAction =
  | "create"
  | "update"
  | "delete"
  | "login"
  | "logout"
  | "export"
  | "invite"
  | "role_change"
  | "settings_change";

export interface AuditLogEntry {
  id: string;
  tenant_id: string;
  user_id: string;
  user_name: string;
  user_email: string;
  action: AuditAction;
  resource_type: string;
  resource_id: string | null;
  details: string | null;
  ip_address: string | null;
  created_at: string;
}

export interface AuditLogListResponse {
  items: AuditLogEntry[];
  total: number;
  page: number;
  page_size: number;
}

export interface AuditLogFilters {
  user_id?: string;
  action?: AuditAction | "";
  resource_type?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export const USER_STATUSES: UserStatus[] = [
  "active",
  "inactive",
  "invited",
  "suspended",
];

export const USER_STATUS_LABELS: Record<UserStatus, string> = {
  active: "Active",
  inactive: "Inactive",
  invited: "Invited",
  suspended: "Suspended",
};

export const AUDIT_ACTIONS: AuditAction[] = [
  "create",
  "update",
  "delete",
  "login",
  "logout",
  "export",
  "invite",
  "role_change",
  "settings_change",
];

export const AUDIT_ACTION_LABELS: Record<AuditAction, string> = {
  create: "Create",
  update: "Update",
  delete: "Delete",
  login: "Login",
  logout: "Logout",
  export: "Export",
  invite: "Invite",
  role_change: "Role Change",
  settings_change: "Settings Change",
};

export const DEFAULT_PERMISSIONS = [
  "vendors:read",
  "vendors:write",
  "vendors:delete",
  "assessments:read",
  "assessments:write",
  "assessments:delete",
  "findings:read",
  "findings:write",
  "findings:close",
  "evidence:read",
  "evidence:upload",
  "evidence:delete",
  "reports:read",
  "reports:generate",
  "monitoring:read",
  "monitoring:manage",
  "admin:users",
  "admin:roles",
  "admin:settings",
  "admin:audit",
] as const;
