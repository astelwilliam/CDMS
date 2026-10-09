import { useEffect, useState } from "react";
import api from "./api";

function App() {
  const [colleges, setColleges] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.get("/colleges/"), api.get("/departments/")])
      .then(([collegesRes, departmentsRes]) => {
        setColleges(collegesRes.data);
        setDepartments(departmentsRes.data);
      })
      .catch((err) => {
        console.log("ERROR:", err);
        console.log("RESPONSE:", err.response);
        console.log("DATA:", err.response?.data);
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, []);

  // Group departments by their college_id
  const departmentsByCollege = departments.reduce((acc, dept) => {
    (acc[dept.college_id] ||= []).push(dept);
    return acc;
  }, {});

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>College Department Management System</h1>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {loading && <p>Loading...</p>}

      <h2>Colleges</h2>

      {!loading && colleges.length === 0 ? (
        <p>No colleges found.</p>
      ) : (
        <ul>
          {colleges
            .filter((college) => college.name && college.name.trim() !== "")
            .map((college) => {
              const collegeDepts = departmentsByCollege[college.id] || [];
              return (
                <li key={college.id} style={{ marginBottom: "12px" }}>
                  <strong>{college.name}</strong>
                  {collegeDepts.length === 0 ? (
                    <p style={{ margin: "4px 0 0 0", color: "#888", fontSize: "14px" }}>
                      No departments yet.
                    </p>
                  ) : (
                    <ul>
                      {collegeDepts.map((dept) => (
                        <li key={dept.id}>{dept.name}</li>
                      ))}
                    </ul>
                  )}
                </li>
              );
            })}
        </ul>
      )}
    </div>
  );
}

export default App;
