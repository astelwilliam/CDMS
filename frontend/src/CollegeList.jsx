import { collegeEmptyMessage } from "./collegeList.js";

export default function CollegeList({ colleges }) {
  if (colleges.length === 0) {
    return <p className="empty-state">{collegeEmptyMessage()}</p>;
  }

  return (
    <div className="record-grid">
      {colleges.map((college) => (
        <article className="record-card" key={college.id}>
          <div className="record-heading">
            <h3>{college.name}</h3>
          </div>
          <p>{college.description || "No description provided."}</p>
          {college.contact_information && (
            <p className="record-meta">{college.contact_information}</p>
          )}
        </article>
      ))}
    </div>
  );
}
