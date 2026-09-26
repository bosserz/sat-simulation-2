import { ArrowRight, BarChart3, Calculator, Clock, Flag, Highlighter, Layers, Target } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";

const MODULES = [
  { section: "Reading & Writing", module: "Module 1", minutes: 32 },
  { section: "Reading & Writing", module: "Module 2", minutes: 32 },
  { section: "Math", module: "Module 1", minutes: 35 },
  { section: "Math", module: "Module 2", minutes: 35 }
];

const FEATURES: { icon: LucideIcon; title: string; body: string }[] = [
  {
    icon: Layers,
    title: "Adaptive modules",
    body: "Module 2 adjusts to how you did on Module 1, just like the real Digital SAT."
  },
  {
    icon: Calculator,
    title: "Real test tools",
    body: "Built-in Desmos calculator, formula reference sheet, highlighter and question navigator."
  },
  {
    icon: BarChart3,
    title: "Detailed reports",
    body: "Scores by domain, priority focus areas and a full explanation for every question."
  },
  {
    icon: Target,
    title: "Topic drills",
    body: "Short focused sets for the skills your report flags, with progress tracked per topic."
  }
];

const STEPS = [
  { title: "Take a full mock", body: "Four timed modules with a break between sections." },
  { title: "Review your report", body: "See exactly which domains cost you points and why." },
  { title: "Drill weak spots", body: "Practice the flagged topics, then retest." }
];

export function HomePage() {
  return (
    <div className="space-y-16 pb-10">
      <section className="overflow-hidden rounded-xl bg-intsight text-white shadow-soft">
        <div className="grid gap-10 p-6 sm:p-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:p-14">
          <div>
            <p className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-sm font-semibold text-teal-200">
              <span className="h-2 w-2 rounded-full bg-teal-300" />
              Digital SAT simulation
            </p>
            <h1 className="max-w-xl text-4xl font-bold leading-tight md:text-5xl">
              Practice the SAT exactly the way you'll take it.
            </h1>
            <p className="mt-5 max-w-lg text-lg text-white/75">
              Full-length adaptive mock tests with the real interface and timing, then clear reports and drills that show you what to work on next.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/login"
                className="inline-flex min-h-11 items-center gap-2 rounded-md bg-teal-400 px-5 py-2 font-semibold text-intsight transition hover:bg-teal-300"
              >
                Log in to start
                <ArrowRight size={18} />
              </Link>
              <Link
                to="/request_account"
                className="inline-flex min-h-11 items-center gap-2 rounded-md border border-white/30 px-5 py-2 font-semibold text-white transition hover:bg-white/10"
              >
                Request an account
              </Link>
            </div>
          </div>
          <TestPreview />
        </div>
      </section>

      <section>
        <SectionHeading eyebrow="Test format" title="Same structure as test day" />
        <ol className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {MODULES.map((m, i) => (
            <li key={i} className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
              <p className="text-sm font-semibold text-aqua">{m.section}</p>
              <p className="mt-1 text-lg font-bold">{m.module}</p>
              <p className="mt-3 flex items-center gap-1.5 text-sm text-slate-500">
                <Clock size={15} />
                {m.minutes} minutes
              </p>
            </li>
          ))}
        </ol>
        <p className="mt-3 text-sm text-slate-500">About 2 hours 14 minutes of testing, with a break between Reading & Writing and Math.</p>
      </section>

      <section>
        <SectionHeading eyebrow="What you get" title="Everything you need to prepare" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map(({ icon: Icon, title, body }) => (
            <div key={title} className="panel">
              <span className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-md bg-teal-50 text-aqua">
                <Icon size={22} />
              </span>
              <h3 className="text-lg font-semibold">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
        <SectionHeading eyebrow="How it works" title="Practice, review, improve" />
        <ol className="grid gap-4">
          {STEPS.map((step, i) => (
            <li key={step.title} className="flex gap-4 rounded-md border border-slate-200 bg-white p-5 shadow-sm">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-intsight font-bold text-white">
                {i + 1}
              </span>
              <div>
                <h3 className="font-semibold">{step.title}</h3>
                <p className="mt-1 text-sm text-slate-600">{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="flex flex-col items-start justify-between gap-6 rounded-xl border border-teal-100 bg-teal-50 p-6 sm:p-10 md:flex-row md:items-center">
        <div>
          <h2 className="text-2xl font-bold">Ready for your first mock test?</h2>
          <p className="mt-2 text-slate-600">Accounts are set up by your Intsight Education administrator.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link to="/login" className="primary-button">
            Log in
            <ArrowRight size={18} />
          </Link>
          <Link to="/request_account" className="secondary-button">Request an account</Link>
        </div>
      </section>
    </div>
  );
}

function SectionHeading({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <div className="mb-6">
      <p className="text-sm font-semibold uppercase tracking-wide text-aqua">{eyebrow}</p>
      <h2 className="mt-1 text-2xl font-bold md:text-3xl">{title}</h2>
    </div>
  );
}

// Decorative sketch of the practice screen so visitors can see what the test looks like.
function TestPreview() {
  return (
    <div aria-hidden="true" className="rounded-lg bg-white p-1.5 text-ink shadow-2xl ring-1 ring-white/20">
      <div className="flex items-center justify-between rounded-t-md border-b border-slate-200 bg-slate-50 px-4 py-2.5">
        <span className="text-xs font-semibold text-slate-600">Math · Module 2</span>
        <span className="flex items-center gap-1 rounded-md bg-white px-2 py-0.5 text-xs font-bold tabular-nums text-slate-700 ring-1 ring-slate-200">
          <Clock size={12} />
          24:18
        </span>
        <span className="flex gap-1.5 text-slate-400">
          <Calculator size={15} />
          <Highlighter size={15} />
        </span>
      </div>
      <div className="grid grid-cols-2 divide-x divide-slate-200">
        <div className="space-y-2 p-4">
          <div className="h-2 w-11/12 rounded bg-slate-200" />
          <div className="h-2 w-full rounded bg-slate-200" />
          <div className="h-2 w-10/12 rounded bg-yellow-200" />
          <div className="h-2 w-full rounded bg-slate-200" />
          <div className="h-2 w-7/12 rounded bg-slate-200" />
          <div className="mt-4 h-16 rounded-md border border-dashed border-slate-300 bg-slate-50" />
        </div>
        <div className="space-y-2 p-4">
          <div className="flex items-center justify-between">
            <span className="rounded bg-intsight px-1.5 text-[10px] font-bold text-white">14</span>
            <Flag size={13} className="text-amber" />
          </div>
          <div className="h-2 w-10/12 rounded bg-slate-300" />
          {["A", "B", "C", "D"].map((letter) => (
            <div
              key={letter}
              className={`flex items-center gap-2 rounded-md border px-2 py-1.5 ${
                letter === "C" ? "border-aqua bg-teal-50" : "border-slate-200"
              }`}
            >
              <span
                className={`flex h-4 w-4 items-center justify-center rounded-full text-[9px] font-bold ${
                  letter === "C" ? "bg-aqua text-white" : "border border-slate-300 text-slate-500"
                }`}
              >
                {letter}
              </span>
              <span className="h-1.5 flex-1 rounded bg-slate-200" />
            </div>
          ))}
        </div>
      </div>
      <div className="flex items-center justify-between rounded-b-md border-t border-slate-200 bg-slate-50 px-4 py-2">
        <span className="text-[10px] font-semibold text-slate-500">Question 14 of 22</span>
        <span className="rounded bg-aqua px-2 py-0.5 text-[10px] font-semibold text-white">Next</span>
      </div>
    </div>
  );
}
