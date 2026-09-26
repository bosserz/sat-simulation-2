import { useEffect, useState } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { api } from "./api/client";
import { supabase } from "./lib/supabase";
import { Layout } from "./components/Layout";
import { Loading } from "./components/Loading";
import { AdminTestsPage } from "./pages/AdminTestsPage";
import { AdminUserDetailPage } from "./pages/AdminUserDetailPage";
import { AdminUsersPage } from "./pages/AdminUsersPage";
import { BreakPage } from "./pages/BreakPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DrillResultsPage } from "./pages/DrillResultsPage";
import { DrillSessionPage } from "./pages/DrillSessionPage";
import { DrillTopicPage } from "./pages/DrillTopicPage";
import { DrillsPage } from "./pages/DrillsPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { PracticePage } from "./pages/PracticePage";
import { ReportPage } from "./pages/ReportPage";
import { RequestAccountPage } from "./pages/RequestAccountPage";
import { ResultsPage } from "./pages/ResultsPage";
import { SelectTestPage } from "./pages/SelectTestPage";
import type { ApiUser } from "./types/api";

function RequireAuth({ user, children }: { user: ApiUser | null; children: JSX.Element }) {
  const location = useLocation();
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  return children;
}

function RequireAdmin({ user, children }: { user: ApiUser | null; children: JSX.Element }) {
  if (!user) return <Navigate to="/login" replace />;
  if (!user.is_admin) return <Navigate to="/dashboard" replace />;
  return children;
}

export default function App() {
  const [user, setUser] = useState<ApiUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function restoreSession() {
      const data = await api.me();
      if (data.user) return data.user;
      // Flask cookie expired but the browser still has a Supabase session:
      // exchange it for a new Flask session instead of asking to log in again.
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return null;
      try {
        return (await api.exchangeSupabaseToken(session.access_token)).user;
      } catch {
        await supabase.auth.signOut({ scope: "local" });
        return null;
      }
    }
    restoreSession().then(setUser).catch(() => setUser(null)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading label="Starting Intsight..." />;

  return (
    <Routes>
      <Route element={<Layout user={user} onLogout={() => setUser(null)} />}>
        <Route index element={<HomePage />} />
        <Route path="/login" element={<LoginPage onLogin={setUser} />} />
        <Route path="/request_account" element={<RequestAccountPage />} />
        <Route path="/dashboard" element={<RequireAuth user={user}><DashboardPage /></RequireAuth>} />
        <Route path="/select_test" element={<RequireAuth user={user}><SelectTestPage /></RequireAuth>} />
        <Route path="/practice" element={<RequireAuth user={user}><PracticePage /></RequireAuth>} />
        <Route path="/break" element={<RequireAuth user={user}><BreakPage /></RequireAuth>} />
        <Route path="/mock_results/:sessionId" element={<RequireAuth user={user}><ResultsPage /></RequireAuth>} />
        <Route path="/report/:sessionId" element={<RequireAuth user={user}><ReportPage /></RequireAuth>} />
        <Route path="/drill_select" element={<RequireAuth user={user}><DrillsPage /></RequireAuth>} />
        <Route path="/drill_topic/:topicName" element={<RequireAuth user={user}><DrillTopicPage /></RequireAuth>} />
        <Route path="/drill/:sessionId" element={<RequireAuth user={user}><DrillSessionPage /></RequireAuth>} />
        <Route path="/drill_results/:sessionId" element={<RequireAuth user={user}><DrillResultsPage /></RequireAuth>} />
        <Route path="/admin" element={<RequireAdmin user={user}><AdminUsersPage /></RequireAdmin>} />
        <Route path="/admin/tests" element={<RequireAdmin user={user}><AdminTestsPage /></RequireAdmin>} />
        <Route path="/admin/user/:userId" element={<RequireAdmin user={user}><AdminUserDetailPage /></RequireAdmin>} />
        <Route path="*" element={<Navigate to={user ? "/dashboard" : "/"} replace />} />
      </Route>
    </Routes>
  );
}
