import { useState } from "react";
import { createFacultyMember, requestErrorMessage } from "./workflows.js";

const initialValues = {
  name: "",
  title: "",
  biography: "",
  contact_information: "",
  profile_image_reference: "",
  department_id: "",
};

export default function FacultyCreateForm({ api, departments, onCreated }) {
  const [values, setValues] = useState(initialValues);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  function updateValue(event) {
    setValues((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    const payload = Object.fromEntries(
      Object.entries(values).map(([key, value]) => [key, value.trim()]),
    );

    try {
      const created = await createFacultyMember(api, payload);
      onCreated(created);
      setValues(initialValues);
    } catch (requestError) {
      setError(requestErrorMessage(requestError));
    } finally {
      setSubmitting(false);
    }
  }

  if (departments.length === 0) return null;

  return (
    <details className="create-panel">
      <summary>Add faculty member</summary>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Name
            <input
              name="name"
              value={values.name}
              onChange={updateValue}
              required
            />
          </label>
          <label>
            Department
            <select
              name="department_id"
              value={values.department_id}
              onChange={updateValue}
              required
            >
              <option value="">Select a department</option>
              {departments.map((department) => (
                <option value={department.id} key={department.id}>
                  {department.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Title
            <input name="title" value={values.title} onChange={updateValue} />
          </label>
          <label>
            Contact information
            <input
              name="contact_information"
              value={values.contact_information}
              onChange={updateValue}
            />
          </label>
        </div>
        <label>
          Biography
          <textarea
            name="biography"
            value={values.biography}
            onChange={updateValue}
            rows="3"
          />
        </label>
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" disabled={submitting}>
          {submitting ? "Saving…" : "Create faculty member"}
        </button>
      </form>
    </details>
  );
}
