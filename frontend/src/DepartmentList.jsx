export default function DepartmentList({ departments, colleges, role }) {
  const collegeNames = new Map(
    colleges.map((college) => [college.id, college.name]),
  );

  if (departments.length === 0) {
    return <p className="empty-state">No authorized departments found.</p>;
  }

  return (
    <div className="record-grid">
      {departments.map((department) => (
        <article className="record-card" key={department.id}>
          <div className="record-heading">
            <h3>{department.name}</h3>
            <span className="tag">
              {role === "department_admin" ? "Assigned" : "Department"}
            </span>
          </div>
          {role === "super_admin" && (
            <p className="record-meta">
              College: {collegeNames.get(department.college_id) || "Unknown"}
            </p>
          )}
          <p>{department.description || "No description provided."}</p>
          {department.contact_information && (
            <p className="record-meta">{department.contact_information}</p>
          )}
        </article>
      ))}
    </div>
  );
}
