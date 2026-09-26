import { Download } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { DomainChart } from "../components/DomainChart";
import { HtmlContent } from "../components/HtmlContent";
import { Loading } from "../components/Loading";
import { imageUrl } from "../lib/format";
import type { ReportPayload } from "../types/api";

export function ReportPage() {
  const { sessionId } = useParams();
  const [report, setReport] = useState<ReportPayload | null>(null);
  const id = Number(sessionId);

  useEffect(() => {
    if (id) api.testReport(id).then(setReport);
  }, [id]);

  if (!report) return <Loading label="Loading report..." />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase text-aqua">{report.practice_test_id}</p>
          <h1 className="text-3xl font-bold">Comprehensive Report</h1>
        </div>
        <div className="flex flex-wrap gap-2">
          <a className="primary-button" href={`/api/tests/${id}/report/pdf`}><Download size={16} />Export PDF</a>
          <Link className="secondary-button" to={`/mock_results/${id}`}>Summary</Link>
        </div>
      </div>

      <section className="panel">
        <div className="grid gap-3 sm:grid-cols-4">
          <div className="score-card"><span>Total</span><strong>{report.total_score}</strong></div>
          <div className="score-card"><span>Reading & Writing</span><strong>{report.verbal_score}</strong></div>
          <div className="score-card"><span>Mathematics</span><strong>{report.math_score}</strong></div>
          <div className="score-card"><span>Raw Correct</span><strong>{report.raw_score}</strong></div>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <DomainChart title="Reading & Writing Domains" data={report.domain_chart_data.verbal} />
        <DomainChart title="Math Domains" data={report.domain_chart_data.math} />
      </div>

      <section className="panel">
        <h2 className="section-title">Priority Focus</h2>
        <div className="grid gap-3 md:grid-cols-3">
          {report.improvement_analysis.priority_focus.map((focus) => (
            <div className="rounded-md border border-slate-200 p-3" key={`${focus.subject_label}-${focus.domain}`}>
              <p className="text-sm text-slate-500">{focus.subject_label}</p>
              <p className="font-semibold">{focus.domain}</p>
              <p className="text-sm text-amber">{focus.pct_correct}% correct</p>
            </div>
          ))}
        </div>
      </section>

      {report.section_reviews.map((section) => (
        <section className="panel" key={section.section_idx}>
          <h2 className="section-title">{section.section.name} ({section.score}/{section.total})</h2>
          <div className="space-y-4">
            {section.questions.map((row) => (
              <details className="rounded-md border border-slate-200 p-4" key={row.qid}>
                <summary className="cursor-pointer font-semibold">
                  Q{row.qid + 1}: {row.is_correct ? "Correct" : "Incorrect"} {row.marked ? "(Marked)" : ""}
                </summary>
                <div className="mt-3 grid gap-3">
                  <HtmlContent className="sat-content" html={row.question.passage} />
                  <HtmlContent className="sat-content font-semibold" html={row.question.question || row.question.text} />
                  {row.question.image && <img className="max-w-full rounded-md" src={imageUrl(row.question.image)} alt="" />}
                  <p className="text-sm"><strong>Your answer:</strong> {row.user_answer || "Not answered"}</p>
                  <p className="text-sm"><strong>Correct answer:</strong> {Array.isArray(row.question.correct_answer) ? row.question.correct_answer.join(", ") : row.question.correct_answer}</p>
                  {row.question.explanation && <HtmlContent className="sat-content rounded-md bg-slate-50 p-3" html={row.question.explanation} />}
                </div>
              </details>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
