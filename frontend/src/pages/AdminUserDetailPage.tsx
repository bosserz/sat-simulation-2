import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";
import { formatDate } from "../lib/format";
import type { AccessGrant } from "../types/api";

const STATUS_STYLES: Record<AccessGrant["status"], string> = {
  active: "bg-teal-100 text-teal-800",
  used_up: "bg-slate-100 text-slate-600",
  expired: "bg-slate-100 text-slate-600",
  revoked: "bg-rose-50 text-rose-700"
};

const STATUS_LABELS: Record<AccessGrant["status"], string> = {
  active: "Active",
  used_up: "Used up",
  expired: "Expired",
  revoked: "Revoked"
};

function GrantForm({ tests, onSubmit }: { tests: string[]; onSubmit: (grant: Parameters<typeof api.createGrant>[1]) => Promise<void> }) {
  const [testId, setTestId] = useState("");
  const [attempts, setAttempts] = useState("");
  const [expiry, setExpiry] = useState("");
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setSaving(true);
    try {
      await onSubmit({
        practice_test_id: testId || null,
        max_attempts: attempts ? Number(attempts) : null,
        // End of the chosen day in the admin's time zone
        expires_at: expiry ? new Date(`${expiry}T23:59:59`).toISOString() : null,
        note
      });
      setAttempts("");
      setExpiry("");
      setNote("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to grant access");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
      <label className="form-label">
        Test
        <select className="form-input" value={testId} onChange={(event) => setTestId(event.target.value)}>
          <option value="">All mock tests</option>
          {tests.map((test) => <option key={test} value={test}>{test}</option>)}
        </select>
      </label>
      <label className="form-label">
        Attempts
        <input className="form-input" type="number" min={1} step={1} placeholder="Unlimited" value={attempts} onChange={(event) => setAttempts(event.target.value)} />
      </label>
      <label className="form-label">
        Expires
        <input className="form-input" type="date" value={expiry} onChange={(event) => setExpiry(event.target.value)} />
      </label>
      <label className="form-label">
        Note
        <input className="form-input" maxLength={255} placeholder="e.g. SAT Intensive, Nov batch" value={note} onChange={(event) => setNote(event.target.value)} />
      </label>
      {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 md:col-span-2">{error}</p>}
      <div className="md:col-span-2">
        <button className="primary-button" disabled={saving}>{saving ? "Granting..." : "Grant access"}</button>
      </div>
    </form>
  );
}

export function AdminUserDetailPage() {
  const { userId } = useParams();
  const [data, setData] = useState<Awaited<ReturnType<typeof api.adminUser>> | null>(null);
  const id = Number(userId);

  function load() {
    return api.adminUser(id).then(setData);
  }

  useEffect(() => {
    if (id) load();
  }, [id]);

  async function grant(newGrant: Parameters<typeof api.createGrant>[1]) {
    await api.createGrant(id, newGrant);
    await load();
  }

  async function revoke(grant: AccessGrant) {
    const scope = grant.practice_test_id ?? "all mock tests";
    if (!window.confirm(`Revoke access to ${scope}? Tests already started can still be finished.`)) return;
    await api.revokeGrant(grant.id);
    await load();
  }

  if (!data) return <Loading label="Loading user..." />;

  return (
    <div className="space-y-6">
      <div>
        <Link className="text-sm font-semibold text-aqua" to="/admin">Back to admin</Link>
        <h1 className="mt-2 text-3xl font-bold">{data.user.username}</h1>
        <p className="text-slate-600">{data.user.email}</p>
      </div>
      <section className="panel space-y-5">
        <div>
          <h2 className="section-title mb-1">Mock test access</h2>
          <p className="text-sm text-slate-600">Each test the student starts uses one attempt. Free tests don't need access.</p>
        </div>
        <GrantForm tests={data.practice_tests} onSubmit={grant} />
        {data.grants.length ? (
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead><tr><th>Test</th><th>Attempts</th><th>Expires</th><th>Status</th><th>Note</th><th>Granted</th><th></th></tr></thead>
              <tbody>
                {data.grants.map((grant) => (
                  <tr key={grant.id}>
                    <td>{grant.practice_test_id ?? "All mock tests"}</td>
                    <td>{grant.attempts_used} / {grant.max_attempts ?? "∞"}</td>
                    <td>{grant.expires_at ? formatDate(grant.expires_at) : "Never"}</td>
                    <td><span className={`rounded px-2 py-1 text-xs font-semibold ${STATUS_STYLES[grant.status]}`}>{STATUS_LABELS[grant.status]}</span></td>
                    <td>{grant.note || "-"}</td>
                    <td>{formatDate(grant.created_at)}</td>
                    <td>{!grant.revoked_at && <button className="font-semibold text-rose-700" onClick={() => revoke(grant)}>Revoke</button>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="empty-text">No access granted yet. This student can only take free tests.</p>
        )}
      </section>
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
