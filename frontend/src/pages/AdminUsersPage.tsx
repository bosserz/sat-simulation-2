import { Settings } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";
import { formatDate } from "../lib/format";

function accessSummary(access: { all_tests: boolean; tests: string[] }) {
  if (access.all_tests) return "All tests";
  if (access.tests.length === 1) return access.tests[0];
  if (access.tests.length) return `${access.tests.length} tests`;
  return "-";
}

export function AdminUsersPage() {
  const [rows, setRows] = useState<any[] | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    api.adminUsers().then((data) => setRows(data.user_stats));
  }, []);

  if (!rows) return <Loading label="Loading admin dashboard..." />;

  const needle = query.trim().toLowerCase();
  const visible = needle
    ? rows.filter((row) => `${row.user.username} ${row.user.email}`.toLowerCase().includes(needle))
    : rows;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">Admin</h1>
          <p className="mt-1 text-slate-600">Review students, their test activity and mock test access.</p>
        </div>
        <Link className="secondary-button" to="/admin/tests"><Settings size={16} />Test settings</Link>
      </div>
      <input className="form-input max-w-md" type="search" placeholder="Search by name or email" value={query} onChange={(event) => setQuery(event.target.value)} />
      <section className="panel overflow-x-auto">
        <table className="data-table">
          <thead><tr><th>User</th><th>Email</th><th>Access</th><th>Total</th><th>Completed</th><th>In Progress</th><th>Latest</th><th></th></tr></thead>
          <tbody>
            {visible.map((row) => (
              <tr key={row.user.id}>
                <td>{row.user.username}</td>
                <td>{row.user.email}</td>
                <td>{row.user.is_admin ? "Admin" : accessSummary(row.access)}</td>
                <td>{row.total}</td>
                <td>{row.completed}</td>
                <td>{row.in_progress}</td>
                <td>{formatDate(row.latest?.start_time)}</td>
                <td><Link className="font-semibold text-aqua" to={`/admin/user/${row.user.id}`}>Manage</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
        {!visible.length && <p className="empty-text mt-4">No students match "{query}".</p>}
      </section>
    </div>
  );
}
