import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { HtmlContent } from "../components/HtmlContent";
import { Loading } from "../components/Loading";

export function DrillResultsPage() {
  const { sessionId } = useParams();
  const [data, setData] = useState<any>(null);
  const id = Number(sessionId);

  useEffect(() => {
    if (id) api.drillResults(id).then(setData);
  }, [id]);

  if (!data) return <Loading label="Loading drill results..." />;

  return (
    <div className="space-y-6">
      <div className="panel">
        <h1 className="text-3xl font-bold">Drill Results</h1>
        <p className="mt-2 text-slate-600">{data.drill_set.topic_name} - Set {data.drill_set.set_number}</p>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <div className="score-card"><span>Accuracy</span><strong>{Math.round(data.drill_session.accuracy_percent)}%</strong></div>
          <div className="score-card"><span>Correct</span><strong>{data.drill_session.correct_count}</strong></div>
          <div className="score-card"><span>Total</span><strong>{data.drill_session.total_count}</strong></div>
        </div>
      </div>
      <section className="panel">
        <h2 className="section-title">Question Review</h2>
        <div className="space-y-3">
          {data.question_results.map((row: any, idx: number) => (
            <details className="rounded-md border border-slate-200 p-4" key={idx}>
              <summary className="cursor-pointer font-semibold">Q{idx + 1}: {row.is_correct ? "Correct" : "Incorrect"}</summary>
              <HtmlContent className="sat-content mt-3" html={row.question.question || row.question.text} />
              <p className="mt-2 text-sm"><strong>Your answer:</strong> {row.user_answer || "Not answered"}</p>
              <p className="text-sm"><strong>Correct answer:</strong> {Array.isArray(row.correct_answer) ? row.correct_answer.join(", ") : row.correct_answer}</p>
            </details>
          ))}
        </div>
      </section>
      <Link className="secondary-button inline-flex" to={`/drill_topic/${encodeURIComponent(data.drill_set.topic_name)}`}>Back to topic</Link>
    </div>
  );
}
