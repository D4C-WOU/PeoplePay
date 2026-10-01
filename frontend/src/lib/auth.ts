// The access token is short-lived and is sent with normal API requests.
const ACCESS_TOKEN_KEY = "peoplepay_access_token";

// The refresh token is used to obtain a new access token after expiry.
const REFRESH_TOKEN_KEY = "peoplepay_refresh_token";

export type UserRole =
  | "ADMIN"
  | "HR_MANAGER"
  | "HR_PAYROLL_MANAGER"
  | "HR_PAYROLL_USER"
  | "EMPLOYEE";

// Keep the labels in one place so the sidebar and other UI components
// do not need to know the internal role codes used by Django.
export const ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: "Administrator",
  HR_MANAGER: "HR Manager",
  HR_PAYROLL_MANAGER: "HR Payroll Manager",
  HR_PAYROLL_USER: "HR Payroll User",
  EMPLOYEE: "Employee",
};

export function getToken(): string | null {
  // localStorage only exists in the browser.
  // Returning null during server rendering prevents Next.js errors.
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setRefreshToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") {
    return;
  }

  // Logging out must remove both JWT tokens.
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function canAccessPayroll(role?: UserRole): boolean {
  return (
    role === "ADMIN" ||
    role === "HR_PAYROLL_MANAGER" ||
    role === "HR_PAYROLL_USER"
  );
}

export function canAccessHR(role?: UserRole): boolean {
  return role === "ADMIN" || role === "HR_MANAGER";
}

export function canWritePayroll(role?: UserRole): boolean {
  return (
    role === "ADMIN" ||
    role === "HR_PAYROLL_MANAGER" ||
    role === "HR_PAYROLL_USER"
  );
}

export function canAccessSalary(role?: UserRole): boolean {
  return (
    role === "ADMIN" ||
    role === "HR_PAYROLL_MANAGER" ||
    role === "HR_PAYROLL_USER"
  );
}

export function canAccessTimeAttendance(role?: UserRole): boolean {
  return (
    role === "ADMIN" ||
    role === "HR_MANAGER" ||
    role === "HR_PAYROLL_MANAGER" ||
    role === "HR_PAYROLL_USER" ||
    role === "EMPLOYEE"
  );
}

export function isSelfServiceOnly(role?: UserRole): boolean {
  return role === "EMPLOYEE";
}