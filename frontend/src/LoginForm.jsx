import { useState } from "react";
import axios from "axios";
import { AuthorizationError } from "./auth.js";

export default function LoginForm({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await onLogin(email.trim(), password);
    } catch (loginError) {
      if (loginError instanceof AuthorizationError) {
        setError(loginError.message);
      } else if (axios.isAxiosError(loginError)) {
        setError(
          loginError.response?.status === 401
            ? "Invalid email or password."
            : "Unable to sign in. Please try again.",
        );
      } else {
        setError("Unable to sign in. Please try again.");
      }
    } finally {
      setPassword("");
      setSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-card" aria-labelledby="login-title">
        <p className="eyebrow">Campus Department Management System</p>
        <h1 id="login-title">Administrator sign in</h1>
        <p className="muted">Use your authorized CDMS administrator account.</p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="username"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}

          <button type="submit" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}
