import { canEditFaculty, facultyRecordStatuses } from "./facultyEditing.js";

export default function FacultyList({ faculty, departments, role, onEdit }) {
  const departmentNames = new Map(
    departments.map((department) => [department.id, department.name]),
  );

  if (faculty.length === 0) {
    return <p className="empty-state">No faculty members found.</p>;
  }

  return (
    <div className="record-grid">
      {faculty.map((member) => (
        <article className="record-card" key={member.id}>
          <div className="record-heading">
            <h3>{member.name}</h3>
            {member.title && <span className="tag">{member.title}</span>}
          </div>
          <p className="record-meta">
            {departmentNames.get(member.department_id) || "Authorized department"}
          </p>
          {facultyRecordStatuses(member, departments).map((status) => (
            <p className="record-meta" key={status}>
              {status}
            </p>
          ))}
          <p>{member.biography || "No biography provided."}</p>
          {member.contact_information && (
            <p className="record-meta">{member.contact_information}</p>
          )}
          {canEditFaculty(role, member, departments) && (
            <div className="record-actions">
              <button
                className="secondary"
                type="button"
                onClick={() => onEdit(member)}
              >
                Edit
              </button>
            </div>
          )}
        </article>
      ))}
    </div>
  );
}
