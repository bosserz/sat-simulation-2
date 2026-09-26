import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";
import { formatDate } from "../lib/format";

export function AdminUsersPage() {
  const [rows, setRows] = useState<any[] | null>(null);

  useEffect(() => {
    api.adminUsers().then((data) => setRows(data.user_stats));
  }, []);

  if (!rows) return <Loading label="Loading admin dashboard..." />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Admin</h1>
        <p className="mt-1 text-slate-600">Review students and their test activity.</p>
      </div>
      <section className="panel overflow-x-auto">
        <table className="data-table">
          <thead><tr><th>User</th><th>Email</th><th>Total</th><th>Completed</th><th>In Progress</th><th>Latest</th><th></th></tr></thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.user.id}>
                <td>{row.user.username}</td>
                <td>{row.user.email}</td>
                <td>{row.total}</td>
                <td>{row.completed}</td>
                <td>{row.in_progress}</td>
                <td>{formatDate(row.latest?.start_time)}</td>
                <td><Link className="font-semibold text-aqua" to={`/admin/user/${row.user.id}`}>View</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
