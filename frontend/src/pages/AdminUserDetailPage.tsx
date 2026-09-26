import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";
import { formatDate } from "../lib/format";

export function AdminUserDetailPage() {
  const { userId } = useParams();
  const [data, setData] = useState<any>(null);
  const id = Number(userId);

  useEffect(() => {
    if (id) api.adminUser(id).then(setData);
  }, [id]);

  if (!data) return <Loading label="Loading user..." />;

  return (
    <div className="space-y-6">
      <div>
        <Link className="text-sm font-semibold text-aqua" to="/admin">Back to admin</Link>
        <h1 className="mt-2 text-3xl font-bold">{data.user.username}</h1>
        <p className="text-slate-600">{data.user.email}</p>
      </div>
      <section className="panel overflow-x-auto">
        <table className="data-table">
          <thead><tr><th>Test</th><th>Date</th><th>Status</th><th>Total</th><th>Reading</th><th>Math</th><th>Actions</th></tr></thead>
          <tbody>
            {data.session_data.map((row: any) => (
              <tr key={row.session.id}>
                <td>{row.session.practice_test_id}</td>
                <td>{formatDate(row.session.start_time)}</td>
                <td>{row.session.is_complete ? "Complete" : "In progress"}</td>
                <td>{row.scores?.total_score || "-"}</td>
                <td>{row.scores?.verbal_score || "-"}</td>
                <td>{row.scores?.math_score || "-"}</td>
                <td>{row.session.is_complete && <Link className="font-semibold text-aqua" to={`/report/${row.session.id}`}>Report</Link>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
