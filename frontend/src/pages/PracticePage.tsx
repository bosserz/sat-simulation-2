import { Calculator, FileText, Flag, Highlighter, ListChecks } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { HtmlContent } from "../components/HtmlContent";
import { Loading } from "../components/Loading";
import { Timer } from "../components/Timer";
import { imageUrl } from "../lib/format";
import { readSelection, type HighlightSelection, type TextHighlight } from "../lib/highlights";
import type { TestState } from "../types/api";

export function PracticePage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [state, setState] = useState<TestState | null>(null);
  const [answer, setAnswer] = useState("");
  const [showStatus, setShowStatus] = useState(false);
  const [showDesmos, setShowDesmos] = useState(false);
  const [showFormula, setShowFormula] = useState(false);
  const [error, setError] = useState("");
  const sessionId = Number(params.get("session"));
  const [highlights, setHighlights] = useState<TextHighlight[]>([]);
  const passageRef = useRef<HTMLDivElement>(null);
  const questionRef = useRef<HTMLDivElement>(null);
  const selectionRef = useRef<HighlightSelection | null>(null);

  useEffect(() => {
    if (sessionId) {
      api.testState(sessionId).then((payload) => {
        setState(payload);
        setAnswer(payload.answer || "");
      }).catch((err) => setError(err.message));
    }
  }, [sessionId]);

  const sectionIdx = state?.section_idx;
  const questionIdx = state?.qid;

  const loadHighlights = useCallback(async () => {
    if (sectionIdx == null || questionIdx == null) return;
    try {
      const payload = await api.highlights(sectionIdx, questionIdx);
      setHighlights(payload.highlights as TextHighlight[]);
    } catch {
      setHighlights([]);
    }
  }, [sectionIdx, questionIdx]);

  useEffect(() => {
    selectionRef.current = null;
    setHighlights([]);
    loadHighlights();
  }, [loadHighlights]);

  // Cache the latest valid selection so tapping the Highlight button (which can clear
  // the selection on touch devices) still has something to save.
  useEffect(() => {
    function onSelectionChange() {
      const current = readSelection({ passage: passageRef.current, question: questionRef.current });
      if (current) selectionRef.current = current;
    }
    document.addEventListener("selectionchange", onSelectionChange);
    return () => document.removeEventListener("selectionchange", onSelectionChange);
  }, []);

  const passageHighlights = useMemo(() => highlights.filter((h) => h.target === "passage"), [highlights]);
  const questionHighlights = useMemo(() => highlights.filter((h) => h.target === "question"), [highlights]);

  const q = state?.question;
  const isMath = state?.section?.type === "math";
  const answerKey = `${state?.section_idx}_${state?.qid}`;
  const answeredKeys = state?.answers || {};
  const markedKeys = state?.marked_for_review || {};

  const save = useCallback(async (nextQuestion?: number, mark?: boolean) => {
    if (!state || state.qid == null) return;
    const payload = await api.answerTest(state.test_session.id, {
      current_question: state.qid,
      answer,
      mark_for_review: mark,
      next_question: nextQuestion
    });
    if (payload.status === "section_complete") navigate(`/break?session=${state.test_session.id}`);
    else if (payload.status === "test_complete") navigate(`/mock_results/${state.test_session.id}`);
    else {
      setState(payload);
      setAnswer(payload.answer || "");
    }
  }, [answer, navigate, state]);

  const questionNumbers = useMemo(() => Array.from({ length: state?.total_questions || 0 }, (_, i) => i), [state?.total_questions]);

  async function highlightSelection() {
    const selection = readSelection({ passage: passageRef.current, question: questionRef.current }) || selectionRef.current;
    if (sectionIdx == null || questionIdx == null || !selection) return;
    try {
      await api.createHighlight({ section_idx: sectionIdx, question_idx: questionIdx, ...selection });
      selectionRef.current = null;
      window.getSelection()?.removeAllRanges();
      await loadHighlights();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Could not save highlight.");
    }
  }

  async function removeHighlight(id: number) {
    try {
      await api.deleteHighlight(id);
    } finally {
      await loadHighlights();
    }
  }

  if (!sessionId) return <p className="empty-text">No test session selected.</p>;
  if (error) return <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>;
  if (!state) return <Loading label="Loading practice session..." />;
  if (!q) return <p className="empty-text">No question available.</p>;

  return (
    <div className="practice-grid">
      <div className="practice-header">
        <div>
          <h1 className="text-lg font-bold">{state.section_name}</h1>
          <p className="text-sm text-slate-500">Question {(state.qid || 0) + 1} of {state.total_questions}</p>
        </div>
        <div className="rounded-md bg-white px-3 py-2 shadow-sm">Time Remaining: <Timer seconds={state.remaining_time || 0} onElapsed={() => save(state.total_questions)} /></div>
      </div>

      <section className="practice-panel">
        {q.passage ? <HtmlContent ref={passageRef} className="sat-content" html={q.passage} highlights={passageHighlights} onHighlightClick={removeHighlight} /> : <p className="text-slate-500">No passage for this question.</p>}
        {q.image && <img className="mt-4 max-w-full rounded-md" src={imageUrl(q.image)} alt="" />}
      </section>

      <section className="practice-panel">
        <div className="mb-4 flex flex-wrap gap-2">
          <button className="tool-button" onClick={() => save(undefined, !state.marked)}><Flag size={16} />{state.marked ? "Unmark" : "Mark"}</button>
          <button className="tool-button" onMouseDown={(event) => event.preventDefault()} onClick={highlightSelection}><Highlighter size={16} />Highlight</button>
          {isMath && <button className="tool-button" onClick={() => setShowDesmos(true)}><Calculator size={16} />Desmos</button>}
          {isMath && <button className="tool-button" onClick={() => setShowFormula(true)}><FileText size={16} />Formula</button>}
        </div>

        <HtmlContent ref={questionRef} className="sat-content mb-4 font-semibold" html={q.question || q.text} highlights={questionHighlights} onHighlightClick={removeHighlight} />
        {q.question_image && <img className="mb-4 max-w-full rounded-md" src={imageUrl(q.question_image)} alt="" />}
        {q.equation && <HtmlContent className="sat-content mb-4" html={q.equation} />}

        {q.options?.length ? (
          <div className="space-y-3">
            {q.options.map((option, idx) => (
              <label className={`answer-option ${answer === option ? "selected" : ""}`} key={option}>
                <input type="radio" name="answer" value={option} checked={answer === option} onChange={() => setAnswer(option)} />
                <span className="font-semibold">{String.fromCharCode(65 + idx)}.</span>
                <HtmlContent html={option} />
              </label>
            ))}
          </div>
        ) : (
          <input className="form-input" value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Enter your answer" />
        )}
      </section>

      <div className="practice-footer">
        <button className="secondary-button" disabled={(state.qid || 0) === 0} onClick={() => save((state.qid || 0) - 1)}>Back</button>
        <button className="secondary-button" onClick={() => setShowStatus(true)}><ListChecks size={16} />{(state.qid || 0) + 1} / {state.total_questions}</button>
        <button className="primary-button" onClick={() => save((state.qid || 0) + 1)}>{(state.qid || 0) + 1 >= (state.total_questions || 0) ? "Submit section" : "Next"}</button>
      </div>

      {showStatus && (
        <div className="modal-backdrop" onClick={() => setShowStatus(false)}>
          <div className="modal-panel" onClick={(event) => event.stopPropagation()}>
            <h2 className="section-title">Question Status</h2>
            <div className="status-grid">
              {questionNumbers.map((idx) => {
                const key = `${state.section_idx}_${idx}`;
                const className = markedKeys[key] ? "review" : answeredKeys[key] ? "answered" : "empty";
                return <button key={idx} className={`status-cell ${className}`} onClick={() => { setShowStatus(false); save(idx); }}>{idx + 1}</button>;
              })}
            </div>
          </div>
        </div>
      )}

      {showDesmos && <div className="modal-backdrop"><div className="modal-panel wide"><button className="secondary-button mb-3" onClick={() => setShowDesmos(false)}>Close</button><iframe title="Desmos" className="h-[70vh] w-full" src="https://www.desmos.com/calculator" /></div></div>}
      {showFormula && <div className="modal-backdrop"><div className="modal-panel"><button className="secondary-button mb-3" onClick={() => setShowFormula(false)}>Close</button><img className="max-h-[70vh] w-full object-contain" src="/static/images/formula_reference.jpg" alt="Reference formula" /></div></div>}
    </div>
  );
}
