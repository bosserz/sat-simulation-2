import { ArrowRight, ClipboardList } from "lucide-react";
import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <section className="grid gap-8 py-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
      <div>
        <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-aqua">SAT practice platform</p>
        <h1 className="max-w-3xl text-4xl font-bold leading-tight text-ink md:text-5xl">Intsight SAT Simulation</h1>
        <p className="mt-4 max-w-2xl text-lg text-slate-600">
          Practice full adaptive-style SAT modules, review detailed performance reports, and focus follow-up work with topic drills.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link to="/login" className="primary-button"><ArrowRight size={18} />Login</Link>
          <Link to="/request_account" className="secondary-button">Request account</Link>
        </div>
      </div>
      <div className="rounded-md border border-slate-200 bg-white p-6 shadow-soft">
        <ClipboardList className="mb-4 text-aqua" size={36} />
        <h2 className="text-xl font-semibold">Built for realistic practice</h2>
        <div className="mt-4 grid gap-3 text-sm text-slate-600">
          <p>Timed modules preserve the current test-taking flow.</p>
          <p>Reports keep scoring and recommendations server-computed.</p>
          <p>Existing student progress remains available through the Flask database.</p>
        </div>
      </div>
    </section>
  );
}
