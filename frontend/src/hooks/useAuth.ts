import { useContext } from "react";
import { AuthContext } from "@/providers/query-provider";

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AppProviders");
  }
  return ctx;
}