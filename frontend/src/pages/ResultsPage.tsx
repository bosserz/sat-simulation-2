import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { DomainChart } from "../components/DomainChart";
import { Loading } from "../components/Loading";

export function ResultsPage() {
  const { sessionId } = useParams();
  const [summary, setSummary] = useState<any>(null);
  const id = Number(sessionId);

  useEffect(() => {
    if (id) api.testSummary(id).then(setSummary);
  }, [id]);

  if (!summary) return <Loading label="Loading results..." />;

  return (
    <div className="space-y-6">
      <div className="panel">
        <p className="text-sm font-semibold uppercase text-aqua">Score Summary</p>
        <h1 className="mt-2 text-4xl font-bold">{summary.total_score}</h1>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <div className="score-card"><span>Reading & Writing</span><strong>{summary.verbal_score}</strong></div>
          <div className="score-card"><span>Mathematics</span><strong>{summary.math_score}</strong></div>
          <div className="score-card"><span>Raw Correct</span><strong>{summary.raw_score}</strong></div>
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link className="primary-button" to={`/report/${id}`}>View comprehensive report</Link>
          <Link className="secondary-button" to="/dashboard">Back to dashboard</Link>
        </div>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <DomainChart title="Reading & Writing Domains" data={summary.domain_chart_data?.verbal} />
        <DomainChart title="Math Domains" data={summary.domain_chart_data?.math} />
      </div>
    </div>
  );
}
