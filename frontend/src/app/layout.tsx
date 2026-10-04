import type { Metadata } from "next";

import "./globals.css";
import { AppProviders } from "@/providers/query-provider";

export const metadata: Metadata = {
  title: "PeoplePay360",
  description: "HR and payroll management workspace.",
};

/**
 * Root layout owns only application-wide concerns:
 * - global styles
 * - document metadata
 * - authentication context
 *
 * The dashboard shell itself belongs to /dashboard/layout.tsx so the
 * login page does not accidentally inherit the sidebar and top bar.
 */
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
