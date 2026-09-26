import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";

export function AdminTestsPage() {
  const [tests, setTests] = useState<Array<{ id: string; is_free: boolean }> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.adminTests().then((data) => setTests(data.tests));
  }, []);

  async function toggle(testId: string, is_free: boolean) {
    setError("");
    try {
      const result = await api.setTestFree(testId, is_free);
      setTests((current) => current && current.map((test) => (test.id === testId ? result.test : test)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update test");
    }
  }

  if (!tests) return <Loading label="Loading tests..." />;

  return (
    <div className="space-y-6">
      <div>
        <Link className="text-sm font-semibold text-aqua" to="/admin">Back to admin</Link>
        <h1 className="mt-2 text-3xl font-bold">Test settings</h1>
        <p className="mt-1 text-slate-600">Free tests are open to every signed-in student. Other tests need access granted per student.</p>
      </div>
      {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
      <section className="panel overflow-x-auto">
        <table className="data-table">
          <thead><tr><th>Test</th><th>Access</th></tr></thead>
          <tbody>
            {tests.map((test) => (
              <tr key={test.id}>
                <td className="font-semibold">{test.id}</td>
                <td>
                  <label className="inline-flex cursor-pointer items-center gap-2">
                    <input type="checkbox" className="h-4 w-4 accent-teal-700" checked={test.is_free} onChange={(event) => toggle(test.id, event.target.checked)} />
                    Free for all students
                  </label>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
