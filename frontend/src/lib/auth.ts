const TOKEN_KEY = "peoplepay_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
}

export type UserRole =
  | "ADMIN"
  | "HR_MANAGER"
  | "MANAGER"
  | "EMPLOYEE"
  | "PAYROLL_MANAGER"
  | "PAYROLL_USER";

export const ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: "Administrator",
  HR_MANAGER: "HR Manager",
  MANAGER: "Manager",
  EMPLOYEE: "Employee",
  PAYROLL_MANAGER: "Payroll Manager",
  PAYROLL_USER: "Payroll User",
};

export function canAccessPayroll(role?: UserRole) {
  return role === "ADMIN" || role === "PAYROLL_MANAGER" || role === "PAYROLL_USER";
}

export function canAccessHR(role?: UserRole) {
  return role === "ADMIN" || role === "HR_MANAGER";
}

export function canWritePayroll(role?: UserRole) {
  return (
    role === "ADMIN" ||
    role === "PAYROLL_MANAGER" ||
    role === "PAYROLL_USER"
  );
}

export function canAccessSalary(role?: UserRole) {
  return (
    role === "ADMIN" ||
    role === "PAYROLL_MANAGER" ||
    role === "PAYROLL_USER"
  );
}

export function canAccessTimeAttendance(role?: UserRole) {
  return (
    role === "ADMIN" ||
    role === "HR_MANAGER" ||
    role === "MANAGER" ||
    role === "EMPLOYEE"
  );
}

export function isSelfServiceOnly(role?: UserRole) {
  return role === "EMPLOYEE";
}