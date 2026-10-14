import { useEffect, useState } from "react";
import axios from "axios";

export default function AdminDashboard({ api, user, onLogout }) {
  const [colleges, setColleges] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      try {
        const departmentRequest = api.get("/departments/");
        const collegeRequest =
          user.role === "super_admin" ? api.get("/colleges/") : null;
        const [departmentResponse, collegeResponse] = await Promise.all([
          departmentRequest,
          collegeRequest,
        ]);

        if (active) {
          setDepartments(departmentResponse.data);
          setColleges(collegeResponse?.data || []);
        }
      } catch (requestError) {
        if (active && axios.isAxiosError(requestError)) {
          if (requestError.response?.status === 403) {
            setError("Your account is not authorized to view this resource.");
          } else if (requestError.response?.status !== 401) {
            setError("CDMS data could not be loaded.");
          }
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadDashboard();
    return () => {
      active = false;
    };
  }, [api, user]);

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">CDMS administration</p>
          <h1>Campus overview</h1>
          <p className="muted">
            Signed in as {user.email} ({user.role})
          </p>
        </div>
        <button className="secondary" type="button" onClick={onLogout}>
          Log out
        </button>
      </header>

      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      {loading ? (
        <p>Loading…</p>
      ) : (
        <div className="summary-grid">
          {user.role === "super_admin" && (
            <section className="summary-card">
              <span>Colleges</span>
              <strong>{colleges.length}</strong>
            </section>
          )}
          <section className="summary-card">
            <span>
              {user.role === "department_admin"
                ? "Assigned departments"
                : "Departments"}
            </span>
            <strong>{departments.length}</strong>
          </section>
        </div>
      )}
    </main>
  );
}
