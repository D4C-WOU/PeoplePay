import { apiRequest } from "@/lib/api";
import { useFetch } from "@/hooks/useFetch";
import type { User } from "@/types/auth";
import type { UserRole } from "@/lib/auth";

export function useUsers() {
  return useFetch<User[]>(() => apiRequest<User[]>("/users"), []);
}

export const userApi = {
  update: (id: string, data: { role?: UserRole; is_active?: boolean }) =>
    apiRequest<User>(`/users/${id}`, { method: "PATCH", body: data }),
};
