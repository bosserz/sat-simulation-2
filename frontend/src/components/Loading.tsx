export function Loading({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex min-h-64 items-center justify-center">
      <div className="rounded-md border border-slate-200 bg-white px-5 py-4 text-sm text-slate-600 shadow-soft">
        {label}
      </div>
    </div>
  );
}
