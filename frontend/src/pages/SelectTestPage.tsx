import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";

export function SelectTestPage() {
  const navigate = useNavigate();
  const [tests, setTests] = useState<string[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.tests().then((data) => setTests(data.practice_tests));
  }, []);

  async function start(practice_test_id: string) {
    setError("");
    try {
      const result = await api.startTest(practice_test_id);
      navigate(`/practice?session=${result.test_session.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to start test");
    }
  }

  if (!tests.length) return <Loading label="Loading tests..." />;

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <h1 className="text-3xl font-bold">Select Practice Test</h1>
        <p className="mt-1 text-slate-600">Start a new timed SAT simulation.</p>
      </div>
      {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
      <div className="grid gap-3">
        {tests.map((test) => (
          <button key={test} className="row-card text-left hover:border-aqua" onClick={() => start(test)}>
            <div>
              <p className="text-lg font-semibold">{test}</p>
              <p className="text-sm text-slate-500">Four timed modules with server-side scoring.</p>
            </div>
            <span className="rounded-md bg-aqua px-3 py-2 text-sm font-semibold text-white">Start</span>
          </button>
        ))}
      </div>
    </div>
  );
}
