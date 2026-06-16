import { createClient } from "@/lib/supabase/client";
import type { ApiResponse, ApiRequestOptions } from "@/lib/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  private async getAuthToken(): Promise<string | null> {
    try {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();
      return session?.access_token ?? null;
    } catch {
      return null;
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    apiOptions?: ApiRequestOptions
  ): Promise<ApiResponse<T>> {
    const { headers: extraHeaders, params, timeout = 30000, signal } = apiOptions ?? {};

    const token = await this.getAuthToken();

    const url = new URL(`${this.baseUrl}${endpoint}`);
    if (params) {
      for (const [key, value] of Object.entries(params)) {
        url.searchParams.append(key, value);
      }
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const combinedSignal = signal
      ? anySignal([controller.signal, signal])
      : controller.signal;

    try {
      const response = await fetch(url.toString(), {
        ...options,
        signal: combinedSignal,
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...extraHeaders,
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw this.createApiError(response.status, errorData);
      }

      const data = await response.json();
      return data as ApiResponse<T>;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ApiError) {
        throw error;
      }

      if ((error as Error).name === "AbortError") {
        throw new ApiError("Request timed out or was cancelled", 408);
      }

      throw new ApiError(
        (error as Error).message || "An unexpected error occurred",
        500
      );
    }
  }

  private createApiError(status: number, data: Partial<ApiError> | null): ApiError {
    const message =
      data?.message || getDefaultErrorMessage(status);
    const errors = data?.errors;
    const error = new ApiError(message, status);
    if (errors) {
      (error as { errors?: typeof errors }).errors = errors;
    }
    return error;
  }

  async get<T>(endpoint: string, options?: ApiRequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: "GET" }, options);
  }

  async post<T>(
    endpoint: string,
    body?: unknown,
    options?: ApiRequestOptions
  ): Promise<ApiResponse<T>> {
    return this.request<T>(
      endpoint,
      {
        method: "POST",
        body: body ? JSON.stringify(body) : undefined,
      },
      options
    );
  }

  async put<T>(
    endpoint: string,
    body?: unknown,
    options?: ApiRequestOptions
  ): Promise<ApiResponse<T>> {
    return this.request<T>(
      endpoint,
      {
        method: "PUT",
        body: body ? JSON.stringify(body) : undefined,
      },
      options
    );
  }

  async patch<T>(
    endpoint: string,
    body?: unknown,
    options?: ApiRequestOptions
  ): Promise<ApiResponse<T>> {
    return this.request<T>(
      endpoint,
      {
        method: "PATCH",
        body: body ? JSON.stringify(body) : undefined,
      },
      options
    );
  }

  async delete<T>(endpoint: string, options?: ApiRequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: "DELETE" }, options);
  }
}

export class ApiError extends Error {
  statusCode: number;
  errors?: Array<{ field: string; message: string; code: string }>;

  constructor(message: string, statusCode: number) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
  }
}

function getDefaultErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return "Bad request. Please check your input.";
    case 401:
      return "Authentication required. Please sign in.";
    case 403:
      return "You do not have permission to perform this action.";
    case 404:
      return "The requested resource was not found.";
    case 409:
      return "A conflict occurred. Please try again.";
    case 422:
      return "Validation failed. Please check your input.";
    case 429:
      return "Too many requests. Please try again later.";
    case 500:
      return "An internal server error occurred.";
    default:
      return "An unexpected error occurred.";
  }
}

function anySignal(signals: AbortSignal[]): AbortSignal {
  const controller = new AbortController();

  for (const signal of signals) {
    if (signal.aborted) {
      controller.abort(signal.reason);
      return controller.signal;
    }
    signal.addEventListener("abort", () => controller.abort(signal.reason), {
      once: true,
    });
  }

  return controller.signal;
}

// Singleton instance
let apiClientInstance: ApiClient | null = null;

export function getApiClient(): ApiClient {
  if (!apiClientInstance) {
    apiClientInstance = new ApiClient(API_BASE_URL);
  }
  return apiClientInstance;
}

export const api = new ApiClient(API_BASE_URL);
export const apiClient = api;
export { ApiClient };
