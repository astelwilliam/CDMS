import { useEffect, useState } from "react";
import api from "./api.js";
import { authService } from "./auth.js";
import AdminDashboard from "./AdminDashboard.jsx";
import LoginForm from "./LoginForm.jsx";
import "./App.css";

export default function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    authService.onUnauthorized(() => setUser(null));
    return () => authService.onUnauthorized(null);
  }, []);

  async function handleLogin(email, password) {
    const authenticatedUser = await authService.login(email, password);
    setUser(authenticatedUser);
  }

  function handleLogout() {
    authService.logout();
    setUser(null);
  }

  return user ? (
    <AdminDashboard api={api} user={user} onLogout={handleLogout} />
  ) : (
    <LoginForm onLogin={handleLogin} />
  );
}
