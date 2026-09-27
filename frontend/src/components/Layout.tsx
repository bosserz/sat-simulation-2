import { BookOpen, LayoutDashboard, LogOut, ShieldCheck } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { supabase } from "../lib/supabase";
import type { ApiUser } from "../types/api";

type LayoutProps = {
  user: ApiUser | null;
  onLogout: () => void;
};

export function Layout({ user, onLogout }: LayoutProps) {
  const navigate = useNavigate();

  async function logout() {
    await api.logout();
    // "local" signs out of this site only, not the course platform
    await supabase.auth.signOut({ scope: "local" });
    onLogout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-paper text-ink">
      <header className="bg-intsight text-white shadow-sm">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <NavLink to={user ? "/dashboard" : "/"} className="flex items-center">
            <img src="/static/intsight-logo-white.png" alt="Intsight" className="h-10 w-auto" />
          </NavLink>
          <nav className="flex flex-wrap items-center gap-2 text-sm">
            {user ? (
              <>
                <span className="mr-2 hidden text-white/80 sm:inline">Hello, {user.username}</span>
                <NavLink className="nav-link" to="/dashboard"><LayoutDashboard size={16} />Dashboard</NavLink>
                <NavLink className="nav-link" to="/select_test"><BookOpen size={16} />Tests</NavLink>
                {user.is_admin && <NavLink className="nav-link" to="/admin"><ShieldCheck size={16} />Admin</NavLink>}
                <button className="nav-link" onClick={logout}><LogOut size={16} />Logout</button>
              </>
            ) : (
              <NavLink className="nav-link" to="/login">Login</NavLink>
            )}
          </nav>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
