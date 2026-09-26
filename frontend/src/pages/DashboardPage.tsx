import { ArrowRight, BookOpen, Target } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";
import { formatDate } from "../lib/format";
import type { TestSession } from "../types/api";

type DashboardData = {
  active_session: TestSession | null;
  test_sessions: TestSession[];
};

export function DashboardPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [drills, setDrills] = useState<{ recent_drills: any[]; topic_progress: any[] } | null>(null);

  useEffect(() => {
    api.tests().then(setData);
    api.drillDashboard().then(setDrills).catch(() => setDrills({ recent_drills: [], topic_progress: [] }));
  }, []);

  async function resume(sessionId: number) {
    const result = await api.resumeTest(sessionId);
    navigate(`/practice?session=${result.test_session.id}`);
  }

  if (!data) return <Loading label="Loading dashboard..." />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="mt-1 text-slate-600">Choose your next practice step or review previous work.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Link to="/select_test" className="action-card border-aqua/30 bg-teal-50">
          <BookOpen className="text-aqua" />
          <div>
            <h2 className="text-xl font-semibold">Full Mock Tests</h2>
            <p className="text-sm text-slate-600">Practice complete SAT exams with all sections and timing.</p>
          </div>
          <ArrowRight className="ml-auto text-aqua" />
        </Link>
        <Link to="/drill_select" className="action-card border-amber/30 bg-amber-50">
          <Target className="text-amber" />
          <div>
            <h2 className="text-xl font-semibold">Short Drills</h2>
            <p className="text-sm text-slate-600">Focus on specific topics with compact question sets.</p>
          </div>
          <ArrowRight className="ml-auto text-amber" />
        </Link>
      </div>

      {data.active_session && (
        <div className="rounded-md border border-yellow-300 bg-yellow-50 p-4">
          <p className="font-semibold">Unfinished test: {data.active_session.practice_test_id}</p>
          <button className="secondary-button mt-3" onClick={() => resume(data.active_session!.id)}>Continue test</button>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="panel">
          <h2 className="section-title">Recent Drills</h2>
          {drills?.recent_drills?.length ? drills.recent_drills.map((drill: any) => (
            <div className="row-card" key={drill.id}>
              <div>
                <p className="font-semibold">{drill.topic_name}</p>
                <p className="text-xs text-slate-500">Set {drill.set_number} - {drill.difficulty}</p>
              </div>
              <p className="font-bold text-aqua">{Math.round(drill.accuracy)}%</p>
            </div>
          )) : <p className="empty-text">No drills completed yet.</p>}
        </section>
        <section className="panel">
          <h2 className="section-title">Topic Progress</h2>
          {drills?.topic_progress?.length ? drills.topic_progress.map((topic: any) => (
            <div className="space-y-1" key={topic.topic_name}>
              <div className="flex justify-between text-sm">
                <span className="font-semibold">{topic.topic_name}</span>
                <span>{topic.completed_sets}/3</span>
              </div>
              <div className="h-2 rounded-full bg-slate-200"><div className="h-2 rounded-full bg-aqua" style={{ width: `${Math.min(100, topic.completed_sets / 3 * 100)}%` }} /></div>
            </div>
          )) : <p className="empty-text">Start a drill to track progress.</p>}
        </section>
      </div>

      <section className="panel">
        <h2 className="section-title">Full Tests Completed</h2>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead><tr><th>Practice Test</th><th>Date</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              {data.test_sessions.map((test) => (
                <tr key={test.id}>
                  <td>{test.practice_test_id}</td>
                  <td>{formatDate(test.start_time)}</td>
                  <td>{test.is_complete ? "Complete" : "In progress"}</td>
                  <td>{test.is_complete ? <Link className="text-aqua font-semibold" to={`/report/${test.id}`}>View report</Link> : <button className="text-aqua font-semibold" onClick={() => resume(test.id)}>Continue</button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
