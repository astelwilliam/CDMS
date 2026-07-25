import { useEffect, useState } from "react";
import api from "./api";

function App() {
  const [colleges, setColleges] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/colleges/")
      .then((response) => {
        setColleges(response.data);
      })
      .catch((err) => {
        console.log("ERROR:", err);
        console.log("MESSAGE:", err.message);
        console.log("RESPONSE:", err.response);
        console.log("REQUEST:", err.request);
        console.log("DATA:", err.response?.data);
      
        setError(err.message);
      });
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>College Department Management System</h1>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <h2>Colleges</h2>

      {colleges.length === 0 ? (
        <p>No colleges found.</p>
      ) : (
        <ul>
          {colleges.map((college) => (
            <li key={college.id}>{college.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;