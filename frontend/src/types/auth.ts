import type { UserRole } from "@/lib/auth";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}