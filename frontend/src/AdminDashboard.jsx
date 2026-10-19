import { useCallback, useEffect, useState } from "react";
import DepartmentList from "./DepartmentList.jsx";
import FacultyCreateForm from "./FacultyCreateForm.jsx";
import FacultyEditForm from "./FacultyEditForm.jsx";
import FacultyList from "./FacultyList.jsx";
import { dashboardHashForView, dashboardViewFromHash } from "./dashboardNavigation.js";
import { refreshEditingFaculty, replaceFacultyMember } from "./facultyEditing.js";
import { loadAdministrativeData, requestErrorMessage } from "./workflows.js";

const views = [
  { id: "overview", label: "Overview" },
  { id: "departments", label: "Departments" },
  { id: "faculty", label: "Faculty" },
];

export default function AdminDashboard({ api, user, onLogout }) {
  const [activeView, setActiveView] = useState(() =>
    dashboardViewFromHash(window.location.hash),
  );
  const [colleges, setColleges] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [editingFaculty, setEditingFaculty] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const data = await loadAdministrativeData(api, user.role);
      setDepartments(data.departments);
      setFaculty(data.faculty);
      setColleges(data.colleges);
    } catch (requestError) {
      setError(requestErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }, [api, user.role]);

  useEffect(() => {
    const syncView = () => setActiveView(dashboardViewFromHash(window.location.hash));
    window.addEventListener("hashchange", syncView);
    window.addEventListener("popstate", syncView);
    return () => {
      window.removeEventListener("hashchange", syncView);
      window.removeEventListener("popstate", syncView);
    };
  }, []);

  useEffect(() => {
    let active = true;
    loadAdministrativeData(api, user.role)
      .then((data) => {
        if (active) {
          setDepartments(data.departments);
          setFaculty(data.faculty);
          setColleges(data.colleges);
        }
      })
      .catch((requestError) => {
        if (active) setError(requestErrorMessage(requestError));
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [api, user.role]);

  function handleFacultyCreated(created) {
    setFaculty((current) => [...current, created]);
  }

  function handleFacultyUpdated(updated) {
    setFaculty((current) => replaceFacultyMember(current, updated));
    setEditingFaculty((current) => refreshEditingFaculty(current, updated));
  }

  function handleRetry() {
    setError("");
    setLoading(true);
    loadData();
  }

  function handleViewChange(view) {
    window.history.pushState(null, "", dashboardHashForView(view));
    setActiveView(view);
  }

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

      <nav className="dashboard-nav" aria-label="Administration sections">
        {views.map((view) => (
          <button
            className={activeView === view.id ? "nav-button active" : "nav-button"}
            type="button"
            aria-pressed={activeView === view.id}
            onClick={() => handleViewChange(view.id)}
            key={view.id}
          >
            {view.label}
          </button>
        ))}
      </nav>

      {error && (
        <div className="error-panel" role="alert">
          <p>{error}</p>
          {error && (
            <button className="secondary" type="button" onClick={handleRetry}>
              Try again
            </button>
          )}
        </div>
      )}

      {loading ? (
        <p className="loading-state">Loading CDMS data…</p>
      ) : (
        !error && (
          <>
            {activeView === "overview" && (
              <section aria-labelledby="overview-heading">
                <h2 id="overview-heading">Overview</h2>
                <div className="summary-grid">
                  {user.role === "super_admin" && (
                    <article className="summary-card">
                      <span>Colleges</span>
                      <strong>{colleges.length}</strong>
                    </article>
                  )}
                  <article className="summary-card">
                    <span>
                      {user.role === "department_admin"
                        ? "Assigned departments"
                        : "Departments"}
                    </span>
                    <strong>{departments.length}</strong>
                  </article>
                  <article className="summary-card">
                    <span>Faculty members</span>
                    <strong>{faculty.length}</strong>
                  </article>
                </div>
              </section>
            )}

            {activeView === "departments" && (
              <section aria-labelledby="departments-heading">
                <div className="section-heading">
                  <div>
                    <h2 id="departments-heading">Departments</h2>
                    <p className="muted">
                      {user.role === "department_admin"
                        ? "Departments currently assigned to your account."
                        : "All active campus departments."}
                    </p>
                  </div>
                </div>
                <DepartmentList
                  departments={departments}
                  colleges={colleges}
                  role={user.role}
                />
              </section>
            )}

            {activeView === "faculty" && (
              <section aria-labelledby="faculty-heading">
                <div className="section-heading">
                  <div>
                    <h2 id="faculty-heading">Faculty</h2>
                    <p className="muted">
                      Faculty from departments your account may access.
                    </p>
                  </div>
                </div>
                <FacultyCreateForm
                  api={api}
                  departments={departments}
                  onCreated={handleFacultyCreated}
                />
                {user.role === "super_admin" && editingFaculty && (
                  <FacultyEditForm
                    api={api}
                    facultyMember={editingFaculty}
                    key={editingFaculty.id}
                    onCancel={() => setEditingFaculty(null)}
                    onUpdated={handleFacultyUpdated}
                  />
                )}
                <FacultyList
                  faculty={faculty}
                  departments={departments}
                  role={user.role}
                  onEdit={setEditingFaculty}
                />
              </section>
            )}
          </>
        )
      )}
    </main>
  );
}
