import type { UserRole } from "@/lib/auth";

/** User account returned by Django's /auth/me/ endpoint. */
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  /** CurrentUserSerializer does not expose account status, so undefined means active. */
  is_active?: boolean;
}

/** Django's default AbstractUser authentication uses username + password. */
export interface LoginPayload {
  username: string;
  password: string;
}

/** SimpleJWT returns these two tokens. */
export interface TokenResponse {
  access: string;
  refresh: string;
}
