import { api } from "./api";

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

interface UserApiResponse {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  roles: Array<{ id: string; name: string; permissions: string[] }>;
  permissions: string[];
}

interface User {
  id: string;
  email: string;
  name: string;
  first_name: string;
  last_name: string;
  role: string;
  permissions: string[];
  tenant_id: string;
}

function mapApiUser(raw: UserApiResponse, tenantId?: string): User {
  const primaryRole = raw.roles?.[0]?.name || "User";
  return {
    id: raw.id,
    email: raw.email,
    name: `${raw.first_name} ${raw.last_name}`.trim(),
    first_name: raw.first_name,
    last_name: raw.last_name,
    role: primaryRole,
    permissions: raw.permissions || [],
    tenant_id: tenantId || "",
  };
}

export async function login(email: string, password: string): Promise<User> {
  const response = await api.post<LoginResponse>("/auth/login", {
    email,
    password,
  });

  localStorage.setItem("access_token", response.access_token);
  localStorage.setItem("refresh_token", response.refresh_token);

  const raw = await api.get<UserApiResponse>("/auth/me");
  return mapApiUser(raw);
}

export function logout(): void {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
}

export async function refreshToken(): Promise<string | null> {
  const refresh = localStorage.getItem("refresh_token");
  if (!refresh) return null;

  try {
    const response = await api.post<LoginResponse>("/auth/refresh", {
      refresh_token: refresh,
    });
    localStorage.setItem("access_token", response.access_token);
    if (response.refresh_token) {
      localStorage.setItem("refresh_token", response.refresh_token);
    }
    return response.access_token;
  } catch {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    return null;
  }
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export async function getCurrentUser(): Promise<User | null> {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const raw = await api.get<UserApiResponse>("/auth/me");
    return mapApiUser(raw);
  } catch {
    return null;
  }
}

export type { User, LoginResponse };
