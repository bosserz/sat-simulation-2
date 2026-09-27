import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";
import type { DrillSet } from "../types/api";

export function DrillTopicPage() {
  const { topicName = "" } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [timed, setTimed] = useState<Record<number, boolean>>({});

  useEffect(() => {
    api.drillTopic(decodeURIComponent(topicName)).then(setData);
  }, [topicName]);

  async function start(setId: number) {
    const result = await api.startDrill(setId, !!timed[setId]);
    navigate(`/drill/${result.drill_session.id}`);
  }

  if (!data) return <Loading label="Loading topic..." />;

  return (
    <div className="space-y-6">
      <div>
        <Link className="text-sm font-semibold text-aqua" to="/drill_select">Back to drills</Link>
        <h1 className="mt-2 text-3xl font-bold">{data.topic_name}</h1>
        <p className="mt-1 text-slate-600">{data.description}</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {data.sets_with_history.map((row: any) => {
          const set = row.drill_set as DrillSet;
          return (
            <div className="panel" key={set.id}>
              <h2 className="text-xl font-semibold">Set {set.set_number}</h2>
              <p className="text-sm text-slate-500">{set.difficulty} difficulty - {set.num_questions} questions</p>
              <p className="mt-3 text-sm text-slate-600">Attempts: {row.attempts} {row.best_score != null ? `- Best ${Math.round(row.best_score)}%` : ""}</p>
              <label className="mt-4 flex items-center gap-2 text-sm">
                <input type="checkbox" checked={!!timed[set.id]} onChange={(event) => setTimed({ ...timed, [set.id]: event.target.checked })} />
                Use timer
              </label>
              <button className="primary-button mt-4" onClick={() => start(set.id)}>Start set</button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
