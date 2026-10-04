import {
  clearToken,
  getRefreshToken,
  getToken,
  setToken,
} from "@/lib/auth";

export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api"
).replace(/\/+$/, "");

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE" | "PUT";
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined | null>;
};

function normalizePath(path: string): string {
  if (!path || path.endsWith("/")) {
    return path;
  }

  return `${path}/`;
}

function buildQuery(params?: RequestOptions["params"]): string {
  if (!params) {
    return "";
  }

  const search = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.append(key, String(value));
    }
  });

  const queryString = search.toString();

  return queryString ? `?${queryString}` : "";
}

async function parseErrorResponse(
  response: Response,
  fallbackMessage: string,
): Promise<string> {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data?.detail) && data.detail[0]?.msg) {
      return data.detail[0].msg;
    }

    if (typeof data?.message === "string") {
      return data.message;
    }

    // Django REST Framework validation errors often look like:
    // { "field": ["This field is required."] }
    if (data && typeof data === "object") {
      const messages = Object.entries(data)
        .flatMap(([field, value]) => {
          if (Array.isArray(value)) {
            return value.map((message) => `${field}: ${message}`);
          }

          return [`${field}: ${String(value)}`];
        })
        .filter(Boolean);

      if (messages.length > 0) {
        return messages.join(" ");
      }
    }
  } catch {
    // Some responses do not contain JSON.
  }

  return fallbackMessage;
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        refresh: refreshToken,
      }),
    });

    if (!response.ok) {
      clearToken();
      return null;
    }

    const data = (await response.json()) as {
      access: string;
    };

    setToken(data.access);

    return data.access;
  } catch {
    clearToken();
    return null;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const token = getToken();

  const headers: Record<string, string> = {};

  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response: Response;

  try {
    response = await fetch(
      `${API_BASE_URL}${normalizePath(path)}${buildQuery(options.params)}`,
      {
        method: options.method ?? "GET",
        headers,
        body:
          options.body !== undefined
            ? JSON.stringify(options.body)
            : undefined,
      },
    );
  } catch {
    throw new ApiError(
      "Could not reach the server. Check that the backend is running.",
      0,
    );
  }

  // Access tokens expire. Before forcing the user to log in again,
  // use the refresh token to obtain a new access token.
  if (response.status === 401 && token) {
    const newAccessToken = await refreshAccessToken();

    if (newAccessToken) {
      const retryHeaders: Record<string, string> = {
        ...headers,
        Authorization: `Bearer ${newAccessToken}`,
      };

      try {
        response = await fetch(
          `${API_BASE_URL}${normalizePath(path)}${buildQuery(options.params)}`,
          {
            method: options.method ?? "GET",
            headers: retryHeaders,
            body:
              options.body !== undefined
                ? JSON.stringify(options.body)
                : undefined,
          },
        );
      } catch {
        throw new ApiError(
          "Could not reach the server. Check that the backend is running.",
          0,
        );
      }
    } else {
      // The refresh token is also invalid/expired, so the session
      // can no longer be recovered automatically.
      clearToken();

      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("peoplepay:session-expired"));
      }

      throw new ApiError(
        "Session expired. Please sign in again.",
        401,
      );
    }
  }

  if (!response.ok) {
    const detail = await parseErrorResponse(
      response,
      response.statusText || "Request failed.",
    );

    throw new ApiError(detail, response.status);
  }

  // DELETE requests commonly return HTTP 204 with no response body.
  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type") ?? "";

  // Some endpoints can return files instead of JSON.
  if (!contentType.includes("application/json")) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function apiDownload(path: string): Promise<Blob> {
  const token = getToken();

  const headers: Record<string, string> = {};

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response = await fetch(`${API_BASE_URL}${normalizePath(path)}`, {
    headers,
  });

  // Downloads can also encounter an expired access token.
  if (response.status === 401 && token) {
    const newAccessToken = await refreshAccessToken();

    if (!newAccessToken) {
      clearToken();

      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("peoplepay:session-expired"));
      }

      throw new ApiError(
        "Session expired. Please sign in again.",
        401,
      );
    }

    response = await fetch(`${API_BASE_URL}${normalizePath(path)}`, {
      headers: {
        Authorization: `Bearer ${newAccessToken}`,
      },
    });
  }

  if (!response.ok) {
    throw new ApiError("Could not download file.", response.status);
  }

  return response.blob();
}