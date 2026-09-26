import type { DrillState, ReportPayload, TestState } from "../types/api";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(init.headers || {})
    },
    ...init
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const message = typeof payload === "object" && payload && "error" in payload
      ? String((payload as { error: unknown }).error)
      : `Request failed (${response.status})`;
    throw new Error(message);
  }

  return payload as T;
}

export const api = {
  me: () => request<{ authenticated: boolean; user: import("../types/api").ApiUser | null }>("/api/me"),
  exchangeSupabaseToken: (access_token: string) => request<{ ok: true; user: import("../types/api").ApiUser }>("/api/auth/supabase", {
    method: "POST",
    body: JSON.stringify({ access_token })
  }),
  logout: () => request<{ ok: true }>("/api/auth/logout", { method: "POST" }),
  tests: () => request<{
    practice_tests: string[];
    active_session: import("../types/api").TestSession | null;
    test_sessions: import("../types/api").TestSession[];
  }>("/api/tests"),
  startTest: (practice_test_id: string) => request<{ ok: true; test_session: import("../types/api").TestSession }>("/api/tests/start", {
    method: "POST",
    body: JSON.stringify({ practice_test_id })
  }),
  resumeTest: (session_id: number) => request<{ ok: true; test_session: import("../types/api").TestSession }>("/api/tests/resume", {
    method: "POST",
    body: JSON.stringify({ session_id })
  }),
  testState: (sessionId: number, startTimer = true) => request<TestState>(`/api/tests/${sessionId}/state${startTimer ? "" : "?start_timer=false"}`),
  answerTest: (sessionId: number, body: Record<string, unknown>) => request<TestState>(`/api/tests/${sessionId}/answer`, {
    method: "POST",
    body: JSON.stringify(body)
  }),
  testSummary: (sessionId: number) => request<Pick<ReportPayload, "test_session" | "raw_score" | "verbal_score" | "math_score" | "total_score" | "domain_chart_data">>(`/api/tests/${sessionId}/summary`),
  testReport: (sessionId: number) => request<ReportPayload>(`/api/tests/${sessionId}/report`),
  highlights: (sectionIdx: number, questionIdx: number) => request<{ highlights: Array<Record<string, unknown>> }>(`/api/highlights?section_idx=${sectionIdx}&question_idx=${questionIdx}`),
  createHighlight: (body: Record<string, unknown>) => request<{ ok: true; highlight: Record<string, unknown> }>("/api/highlights", {
    method: "POST",
    body: JSON.stringify(body)
  }),
  clearHighlights: (section_idx: number, question_idx: number) => request<{ ok: true }>("/api/highlights/clear", {
    method: "DELETE",
    body: JSON.stringify({ section_idx, question_idx })
  }),
  deleteHighlight: (id: number) => request<{ ok: true }>(`/api/highlights/${id}`, { method: "DELETE" }),
  drillDashboard: () => request<{ recent_drills: unknown[]; topic_progress: unknown[] }>("/api/drill/dashboard"),
  drillTopics: () => request<{ topics_by_section: Record<string, unknown[]> }>("/api/drills/topics"),
  drillTopic: (topicName: string) => request<{ topic_name: string; description: string; sets_with_history: Array<Record<string, unknown>> }>(`/api/drills/topics/${encodeURIComponent(topicName)}`),
  startDrill: (drillSetId: number, use_timer: boolean) => request<{ ok: true; drill_session: import("../types/api").DrillSession }>(`/api/drills/${drillSetId}/start`, {
    method: "POST",
    body: JSON.stringify({ use_timer })
  }),
  drillState: (sessionId: number) => request<DrillState>(`/api/drills/sessions/${sessionId}/state`),
  answerDrill: (sessionId: number, body: Record<string, unknown>) => request<DrillState>(`/api/drills/sessions/${sessionId}/answer`, {
    method: "POST",
    body: JSON.stringify(body)
  }),
  drillResults: (sessionId: number) => request<Record<string, unknown>>(`/api/drills/sessions/${sessionId}/results`),
  adminUsers: () => request<{ user_stats: Array<Record<string, unknown>> }>("/api/admin/users"),
  adminUser: (userId: number) => request<{ user: import("../types/api").ApiUser; session_data: Array<Record<string, unknown>> }>(`/api/admin/users/${userId}`)
};
