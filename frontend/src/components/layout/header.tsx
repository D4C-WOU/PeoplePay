export function Header({
  title,
  description,
  actions,
  eyebrow = "People operations",
}: {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  eyebrow?: string;
}) {
  return (
    <div className="relative overflow-hidden border-b border-[var(--pp-border)] bg-white px-4 py-6 sm:px-7">
      <div className="pp-accent-strip absolute inset-x-0 top-0 h-[3px]" />
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="mb-1.5 inline-flex items-center gap-1.5 rounded-full bg-[var(--pp-brand-light)] px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.08em] text-[var(--pp-brand)]">
            {eyebrow}
          </p>
          <h1 className="text-[1.6rem] font-semibold tracking-tight text-slate-900">
            {title}
          </h1>
          {description && (
            <p className="mt-1.5 max-w-2xl text-sm text-slate-500">
              {description}
            </p>
          )}
        </div>
        {actions && (
          <div className="flex w-full flex-wrap items-center gap-2 sm:w-auto">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
