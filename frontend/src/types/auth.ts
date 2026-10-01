import type { UserRole } from "@/lib/auth";

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export interface LoginPayload {
  email: string;
  password: string;
}

// Django SimpleJWT returns "access" and "refresh".
// The previous frontend expected "access_token", which belonged
// to the previous authentication contract.
export interface TokenResponse {
  access: string;
  refresh: string;
}