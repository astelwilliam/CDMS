import { useEffect, useState } from "react";
import api from "./api.js";
import { authService } from "./auth.js";
import AdminDashboard from "./AdminDashboard.jsx";
import LoginForm from "./LoginForm.jsx";
import "./App.css";

export default function App() {
  const [user, setUser] = useState(undefined);

  useEffect(() => {
    authService.onUnauthorized(() => setUser(null));
    let active = true;
    authService.restore()
      .then((restoredUser) => {
        if (active) setUser(restoredUser);
      })
      .catch(() => {
        if (active) setUser(null);
      });
    return () => {
      active = false;
      authService.onUnauthorized(null);
    };
  }, []);

  async function handleLogin(email, password) {
    const authenticatedUser = await authService.login(email, password);
    setUser(authenticatedUser);
  }

  async function handleLogout() {
    try {
      await authService.logout();
    } finally {
      setUser(null);
    }
  }

  if (user === undefined) {
    return <main className="login-page"><p>Restoring session…</p></main>;
  }

  return user ? (
    <AdminDashboard api={api} user={user} onLogout={handleLogout} />
  ) : (
    <LoginForm onLogin={handleLogin} />
  );
}
