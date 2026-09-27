import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";
import { HtmlContent } from "../components/HtmlContent";
import { Loading } from "../components/Loading";
import { Timer } from "../components/Timer";
import type { DrillState } from "../types/api";

export function DrillSessionPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const id = Number(sessionId);
  const [state, setState] = useState<DrillState | null>(null);
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  useEffect(() => {
    if (id) api.drillState(id).then((payload) => {
      setState(payload);
      setAnswers(payload.answers || {});
    });
  }, [id]);

  async function save(nextIdx: number) {
    if (!state) return;
    const q = state.questions[idx];
    const result = await api.answerDrill(id, {
      current_question: idx,
      question_id: q?.question_id,
      answer: q?.question_id ? answers[String(q.question_id)] : null,
      next_question: nextIdx
    });
    if (result.status === "drill_complete") navigate(`/drill_results/${id}`);
    else {
      setState(result);
      setIdx(nextIdx);
    }
  }

  if (!state) return <Loading label="Loading drill..." />;
  const q = state.questions[idx];
  const value = q?.question_id ? answers[String(q.question_id)] || "" : "";

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="panel">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold">{state.drill_set.topic_name}</h1>
            <p className="text-sm text-slate-500">Set {state.drill_set.set_number} - Question {idx + 1} of {state.total_questions}</p>
          </div>
          {state.drill_session.use_timer && <div className="rounded-md bg-slate-50 px-3 py-2">Time: <Timer seconds={state.total_questions * 120} onElapsed={() => save(state.total_questions)} /></div>}
        </div>
        <div className="mt-4 h-2 rounded-full bg-slate-200"><div className="h-2 rounded-full bg-aqua" style={{ width: `${((idx + 1) / state.total_questions) * 100}%` }} /></div>
      </div>

      <section className="panel">
        {q.passage && <HtmlContent className="sat-content mb-4 rounded-md bg-slate-50 p-4" html={q.passage} />}
        <HtmlContent className="sat-content mb-4 text-lg font-semibold" html={q.question || q.text} />
        {q.options?.length ? (
          <div className="space-y-3">
            {q.options.map((option, optionIdx) => (
              <label className={`answer-option ${value === option ? "selected" : ""}`} key={option}>
                <input type="radio" checked={value === option} onChange={() => q.question_id && setAnswers({ ...answers, [String(q.question_id)]: option })} />
                <span className="font-semibold">{String.fromCharCode(65 + optionIdx)}.</span>
                <HtmlContent html={option} />
              </label>
            ))}
          </div>
        ) : (
          <input className="form-input" value={value} onChange={(event) => q.question_id && setAnswers({ ...answers, [String(q.question_id)]: event.target.value })} />
        )}
      </section>

      <div className="flex justify-between">
        <button className="secondary-button" disabled={idx === 0} onClick={() => save(idx - 1)}>Previous</button>
        <button className="primary-button" onClick={() => save(idx + 1)}>{idx + 1 >= state.total_questions ? "Finish drill" : "Next"}</button>
      </div>
    </div>
  );
}
