import { Bell, Building2, Globe2, LockKeyhole, Settings2 } from "lucide-react";

import { Header } from "@/components/layout/header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const areas = [
  {
    icon: Building2,
    title: "Workspace",
    description: "Company profile and workspace configuration.",
  },
  {
    icon: Globe2,
    title: "Regional",
    description: "Currency, locale and regional preferences.",
  },
  {
    icon: Bell,
    title: "Notifications",
    description: "Email and operational notification preferences.",
  },
  {
    icon: LockKeyhole,
    title: "Security",
    description: "Access and authentication controls.",
  },
];

export default function SettingsPage() {
  return (
    <div className="pp-page flex flex-1 flex-col">
      <Header
        title="Settings"
        description="Manage workspace preferences and platform configuration."
        eyebrow="Workspace"
      />
      <div className="pp-page-content flex-1 p-4 sm:p-6">
        <div className="mx-auto w-full max-w-[1100px] space-y-5">
          <div className="settings-intro app-surface">
            <div className="settings-intro-icon">
              <Settings2 className="size-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">
                Workspace configuration
              </p>
              <p className="mt-1 text-sm text-slate-500">
                Settings are not yet configurable from this screen. The sections
                below show the intended configuration areas.
              </p>
            </div>
          </div>
          <div className="settings-grid">
            {areas.map(({ icon: Icon, title, description }) => (
              <Card key={title} className="settings-card">
                <CardHeader>
                  <div className="settings-card-icon">
                    <Icon className="size-5" />
                  </div>
                  <CardTitle className="text-sm">{title}</CardTitle>
                </CardHeader>
                <CardContent className="pt-0 text-sm text-slate-500">
                  {description}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
