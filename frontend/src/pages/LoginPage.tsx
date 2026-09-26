import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { coursePlatformUrl, supabase } from "../lib/supabase";
import type { ApiUser } from "../types/api";

type LoginPageProps = {
  onLogin: (user: ApiUser) => void;
};

export function LoginPage({ onLogin }: LoginPageProps) {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const { data, error: authError } = await supabase.auth.signInWithPassword({ email: email.trim(), password });
      if (authError || !data.session) throw new Error(authError?.message || "Unable to log in");
      try {
        const result = await api.exchangeSupabaseToken(data.session.access_token);
        onLogin(result.user);
        navigate("/dashboard");
      } catch (err) {
        // Don't keep a Supabase session the backend refused. "local" leaves the
        // student's other sessions (e.g. the course platform) signed in.
        await supabase.auth.signOut({ scope: "local" });
        throw err;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to log in");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md rounded-md border border-slate-200 bg-white p-6 shadow-soft">
      <h1 className="text-2xl font-bold">Login</h1>
      <p className="mt-2 text-sm text-slate-600">Use the same email and password as your Intsight online course account.</p>
      <form className="mt-6 space-y-4" onSubmit={submit}>
        <label className="form-label">
          Email
          <input className="form-input" type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" />
        </label>
        <label className="form-label">
          Password
          <input className="form-input" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" />
        </label>
        {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
        <button className="primary-button w-full justify-center" disabled={loading}>{loading ? "Logging in..." : "Login"}</button>
      </form>
      {coursePlatformUrl && (
        <p className="mt-4 text-center text-sm text-slate-600">
          Forgot your password? <a className="font-semibold text-aqua" href={coursePlatformUrl}>Reset it on the course platform</a>
        </p>
      )}
      <p className="mt-2 text-center text-sm text-slate-600">
        Don&apos;t have an account? <Link className="font-semibold text-aqua" to="/request_account">Request account</Link>
      </p>
    </div>
  );
}
