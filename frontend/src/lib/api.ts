import {
  clearToken,
  getRefreshToken,
  getToken,
  setToken,
} from "@/lib/auth";


/**
 * Base URL for the Django REST API.
 *
 * Development:
 * http://localhost:8000/api
 *
 * Production deployments can override this through
 * NEXT_PUBLIC_API_URL.
 */
export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api"
).replace(/\/+$/, "");


export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}


type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE" | "PUT";

  body?: unknown;

  params?: Record<
    string,
    string | number | boolean | undefined | null
  >;
};


/**
 * Django's DefaultRouter and API paths use trailing slashes.
 *
 * Keeping this in one place means individual pages do not have to
 * remember whether an endpoint requires a slash.
 */
function normalizePath(path: string): string {
  if (!path || path.endsWith("/")) {
    return path;
  }

  return `${path}/`;
}


/**
 * Convert an object into a URL query string.
 */
function buildQuery(params?: RequestOptions["params"]): string {
  if (!params) {
    return "";
  }

  const search = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (
      value !== undefined &&
      value !== null &&
      value !== ""
    ) {
      search.append(key, String(value));
    }
  });

  const queryString = search.toString();

  return queryString ? `?${queryString}` : "";
}


/**
 * Convert Django REST Framework error responses into a readable message.
 *
 * DRF validation errors commonly look like:
 *
 * {
 *   "field_name": ["This field is required."]
 * }
 */
async function parseErrorResponse(
  response: Response,
  fallbackMessage: string,
): Promise<string> {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (typeof data?.message === "string") {
      return data.message;
    }

    if (Array.isArray(data?.detail) && data.detail[0]?.msg) {
      return data.detail[0].msg;
    }

    if (data && typeof data === "object") {
      const messages = Object.entries(data)
        .flatMap(([field, value]) => {
          if (Array.isArray(value)) {
            return value.map(
              (message) => `${field}: ${message}`,
            );
          }

          return [`${field}: ${String(value)}`];
        })
        .filter(Boolean);

      if (messages.length > 0) {
        return messages.join(" ");
      }
    }
  } catch {
    // Some server responses do not contain JSON.
  }

  return fallbackMessage;
}


/**
 * Ask Django for a new access token using the stored refresh token.
 */
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/auth/refresh/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      },
    );

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


/**
 * Main API request helper used throughout the frontend.
 *
 * Responsibilities:
 * - attach JWT access token
 * - build query parameters
 * - serialize JSON request bodies
 * - refresh expired access tokens
 * - normalize DRF errors
 * - notify the auth provider when the session is unrecoverable
 */
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

  const url =
    `${API_BASE_URL}` +
    `${normalizePath(path)}` +
    `${buildQuery(options.params)}`;

  let response: Response;

  try {
    response = await fetch(url, {
      method: options.method ?? "GET",
      headers,
      body:
        options.body !== undefined
          ? JSON.stringify(options.body)
          : undefined,
    });
  } catch {
    throw new ApiError(
      "Could not reach the server. Check that the Django backend is running on port 8000.",
      0,
    );
  }

  /*
   * If the access token expired, try the refresh token once.
   */
  if (response.status === 401 && token) {
    const newAccessToken = await refreshAccessToken();

    if (newAccessToken) {
      try {
        response = await fetch(url, {
          method: options.method ?? "GET",
          headers: {
            ...headers,
            Authorization: `Bearer ${newAccessToken}`,
          },
          body:
            options.body !== undefined
              ? JSON.stringify(options.body)
              : undefined,
        });
      } catch {
        throw new ApiError(
          "Could not reach the server. Check that the Django backend is running on port 8000.",
          0,
        );
      }
    } else {
      clearToken();

      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new Event("peoplepay:session-expired"),
        );
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

  /*
   * DELETE requests often return 204 with no body.
   */
  if (response.status === 204) {
    return undefined as T;
  }

  const contentType =
    response.headers.get("content-type") ?? "";

  /*
   * File endpoints return blobs instead of JSON.
   */
  if (!contentType.includes("application/json")) {
    return undefined as T;
  }

  return (await response.json()) as T;
}


/**
 * Download a file from an authenticated Django endpoint.
 */
export async function apiDownload(
  path: string,
): Promise<Blob> {
  const token = getToken();

  const url =
    `${API_BASE_URL}${normalizePath(path)}`;

  let response = await fetch(url, {
    headers: token
      ? {
          Authorization: `Bearer ${token}`,
        }
      : {},
  });

  /*
   * Try the refresh token once when the access token expired.
   */
  if (response.status === 401 && token) {
    const newAccessToken = await refreshAccessToken();

    if (!newAccessToken) {
      clearToken();

      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new Event("peoplepay:session-expired"),
        );
      }

      throw new ApiError(
        "Session expired. Please sign in again.",
        401,
      );
    }

    response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${newAccessToken}`,
      },
    });
  }

  if (!response.ok) {
    const detail = await parseErrorResponse(
      response,
      "Could not download the requested file.",
    );

    throw new ApiError(detail, response.status);
  }

  return response.blob();
}