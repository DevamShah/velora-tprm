/**
 * Velora TPRM — API Client
 *
 * Supports two modes controlled by NEXT_PUBLIC_USE_BFF:
 *   - "true"  (production): requests go through the BFF with httpOnly cookies
 *   - "false" (dev default): direct API calls with localStorage JWT tokens
 *
 * In BFF mode the browser never sees or stores JWT tokens — the BFF
 * manages them server-side in Redis and authenticates via a session cookie.
 */

const USE_BFF = process.env.NEXT_PUBLIC_USE_BFF === "true";

const API_BASE_URL = USE_BFF
  ? (process.env.NEXT_PUBLIC_BFF_URL || "/api/v1")
  : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1");

interface ApiRequestOptions extends RequestInit {
  params?: Record<string, string>;
}

interface ApiError {
  status: number;
  message: string;
  details?: unknown;
}

class ApiClient {
  private baseUrl: string;
  private useBff: boolean;

  constructor(baseUrl: string, useBff: boolean) {
    this.baseUrl = baseUrl;
    this.useBff = useBff;
  }

  private getAuthToken(): string | null {
    if (this.useBff) return null; // BFF mode uses cookies, not tokens
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private buildUrl(path: string, params?: Record<string, string>): string {
    const url = new URL(`${this.baseUrl}${path}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.set(key, value);
      });
    }
    return url.toString();
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (response.status === 401) {
      if (!this.useBff && typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      }
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw { status: 401, message: "Unauthorized" } as ApiError;
    }

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw {
        status: response.status,
        message: body.detail || body.message || "Request failed",
        details: body,
      } as ApiError;
    }

    if (response.status === 204) return undefined as T;
    return response.json();
  }

  async request<T>(
    method: string,
    path: string,
    options: ApiRequestOptions = {}
  ): Promise<T> {
    const { params, body, headers: customHeaders, ...rest } = options;
    const token = this.getAuthToken();

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...((customHeaders as Record<string, string>) || {}),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const fetchOptions: RequestInit = {
      method,
      headers,
      body: body ? (typeof body === "string" ? body : JSON.stringify(body)) : undefined,
      ...rest,
    };

    // In BFF mode, include cookies with every request
    if (this.useBff) {
      fetchOptions.credentials = "include";
    }

    const response = await fetch(this.buildUrl(path, params), fetchOptions);

    return this.handleResponse<T>(response);
  }

  async get<T>(path: string, params?: Record<string, string>): Promise<T> {
    return this.request<T>("GET", path, { params });
  }

  async post<T>(path: string, data?: unknown): Promise<T> {
    return this.request<T>("POST", path, {
      body: JSON.stringify(data),
    });
  }

  async put<T>(path: string, data?: unknown): Promise<T> {
    return this.request<T>("PUT", path, {
      body: JSON.stringify(data),
    });
  }

  async patch<T>(path: string, data?: unknown): Promise<T> {
    return this.request<T>("PATCH", path, {
      body: JSON.stringify(data),
    });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>("DELETE", path);
  }

  upload(
    path: string,
    file: File,
    onProgress?: (percent: number) => void
  ): Promise<unknown> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const token = this.getAuthToken();
      const formData = new FormData();
      formData.append("file", file);

      xhr.open("POST", this.buildUrl(path));

      if (token) {
        xhr.setRequestHeader("Authorization", `Bearer ${token}`);
      }

      // In BFF mode, send cookies
      if (this.useBff) {
        xhr.withCredentials = true;
      }

      xhr.upload.addEventListener("progress", (event) => {
        if (event.lengthComputable && onProgress) {
          onProgress(Math.round((event.loaded / event.total) * 100));
        }
      });

      xhr.addEventListener("load", () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText));
        } else if (xhr.status === 401) {
          if (!this.useBff) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
          }
          window.location.href = "/login";
          reject({ status: 401, message: "Unauthorized" });
        } else {
          reject({
            status: xhr.status,
            message: "Upload failed",
          });
        }
      });

      xhr.addEventListener("error", () => {
        reject({ status: 0, message: "Network error" });
      });

      xhr.send(formData);
    });
  }
}

export const api = new ApiClient(API_BASE_URL, USE_BFF);
export { USE_BFF };
export type { ApiError };
