import { Lock } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";
import type { MockTestAccess } from "../types/api";

function accessLabel(test: MockTestAccess) {
  if (!test.has_access) return "Locked. Ask your teacher to unlock this test.";
  if (test.is_free) return "Free test";
  if (test.attempts_left == null) return "Unlocked";
  return `${test.attempts_left} attempt${test.attempts_left === 1 ? "" : "s"} left`;
}

export function SelectTestPage() {
  const navigate = useNavigate();
  const [tests, setTests] = useState<MockTestAccess[] | null>(null);
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

  if (!tests) return <Loading label="Loading tests..." />;

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <h1 className="text-3xl font-bold">Select Practice Test</h1>
        <p className="mt-1 text-slate-600">Start a new timed SAT simulation.</p>
      </div>
      {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
      <div className="grid gap-3">
        {tests.map((test) => (
          <button
            key={test.id}
            className={`row-card text-left ${test.has_access ? "hover:border-aqua" : "cursor-not-allowed bg-slate-50"}`}
            onClick={() => start(test.id)}
            disabled={!test.has_access}
          >
            <div>
              <p className={`text-lg font-semibold ${test.has_access ? "" : "text-slate-500"}`}>{test.id}</p>
              <p className="text-sm text-slate-500">Four timed modules with server-side scoring · {accessLabel(test)}</p>
            </div>
            {test.has_access ? (
              <span className="rounded-md bg-aqua px-3 py-2 text-sm font-semibold text-white">Start</span>
            ) : (
              <span className="inline-flex items-center gap-1 rounded-md bg-slate-200 px-3 py-2 text-sm font-semibold text-slate-600">
                <Lock size={14} />Locked
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
