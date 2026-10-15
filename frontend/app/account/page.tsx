"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/client-api";

type User = {
  id: number;
  username: string;
  email: string;
};

export default function Account() {
  const [user, setUser] = useState<User | null>(null);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<User>("auth/me/")
      .then(setUser)
      .catch(() => {});
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");

    try {
      if (mode === "register") {
        await api("auth/register/", "POST", { username, email, password });
      }
      await api("auth/login/", "POST", { username, password });
      const current = await api<User>("auth/me/");
      setUser(current);
      setPassword("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    try {
      await api("auth/logout/", "POST");
      setUser(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <main className="evu-panel">
      <p className="eyebrow">EVU PRIVATE CLIENT</p>
      <h1>My account</h1>

      {user ? (
        <section className="evu-account-details">
          <p className="evu-welcome">
            Welcome, <strong>{user.username}</strong>.
          </p>
          <p className="evu-email">{user.email}</p>
          <p>
            <Link href="/cart" className="evu-text-link">
              View your bag →
            </Link>
          </p>
          <button type="button" className="evu-button" onClick={logout}>
            Sign out
          </button>
        </section>
      ) : (
        <section>
          <div className="evu-tabs" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={mode === "login"}
              className={mode === "login" ? "active" : ""}
              onClick={() => {
                setMode("login");
                setError("");
              }}
            >
              Sign in
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === "register"}
              className={mode === "register" ? "active" : ""}
              onClick={() => {
                setMode("register");
                setError("");
              }}
            >
              Create account
            </button>
          </div>

          <form onSubmit={submit} className="evu-form">
            <label>
              Username
              <input
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
              />
            </label>

            {mode === "register" && (
              <label>
                Email
                <input
                  required
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                />
              </label>
            )}

            <label>
              Password
              <input
                required
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={
                  mode === "login" ? "current-password" : "new-password"
                }
              />
            </label>

            <button type="submit" className="evu-button" disabled={busy}>
              {busy
                ? "Please wait..."
                : mode === "login"
                  ? "Sign in"
                  : "Create account"}
            </button>
          </form>
        </section>
      )}

      {error && (
        <p role="alert" className="evu-error">
          {error}
        </p>
      )}
    </main>
  );
}