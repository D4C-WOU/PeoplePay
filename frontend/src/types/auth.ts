import type { UserRole } from "@/lib/auth";

/**
 * User account returned by Django's /auth/me/ endpoint.
 *
 * The backend's CurrentUserSerializer returns:
 * id, username, email, first_name, last_name and role.
 */
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;

  /**
   * The current Django serializer does not return is_active.
   *
   * Keep this optional so the frontend does not pretend that the
   * backend provides a field that it currently does not expose.
   */
  is_active?: boolean;
}

/**
 * Django's default AbstractUser authentication uses username + password.
 */
export interface LoginPayload {
  username: string;
  password: string;
}

/**
 * SimpleJWT returns both tokens after successful authentication.
 */
export interface TokenResponse {
  access: string;
  refresh: string;
}