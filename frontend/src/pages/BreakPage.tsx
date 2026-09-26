import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";
import type { TestState } from "../types/api";

export function BreakPage() {
  const [params] = useSearchParams();
  const [state, setState] = useState<TestState | null>(null);
  const sessionId = Number(params.get("session"));

  useEffect(() => {
    if (sessionId) api.testState(sessionId, false).then(setState);
  }, [sessionId]);

  if (!sessionId) return <p className="empty-text">No test session selected.</p>;
  if (!state) return <Loading label="Preparing next section..." />;

  return (
    <div className="mx-auto max-w-xl rounded-md border border-slate-200 bg-white p-6 text-center shadow-soft">
      <h1 className="text-2xl font-bold">Section Break</h1>
      <p className="mt-3 text-slate-600">Next section: <strong>{state.section_name}</strong></p>
      <Link to={`/practice?session=${sessionId}`} className="primary-button mt-6 inline-flex">Start next section</Link>
    </div>
  );
}
