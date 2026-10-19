import { useRef, useState } from "react";
import { facultyEditValues, facultyUpdateErrorMessage } from "./facultyEditing.js";
import { updateFacultyMember } from "./workflows.js";

export default function FacultyEditForm({ api, facultyMember, onCancel, onUpdated }) {
  const [values, setValues] = useState(() => facultyEditValues(facultyMember));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const submissionInProgress = useRef(false);

  function updateValue(event) {
    setValues((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (submissionInProgress.current) return;

    submissionInProgress.current = true;
    setSubmitting(true);
    setError("");
    setSuccess("");

    const payload = Object.fromEntries(
      Object.entries(values).map(([key, value]) => [key, value.trim()]),
    );

    try {
      const updated = await updateFacultyMember(api, facultyMember.id, payload);
      setValues(facultyEditValues(updated));
      setSuccess("Faculty member updated.");
      onUpdated(updated);
    } catch (requestError) {
      setError(facultyUpdateErrorMessage(requestError));
    } finally {
      submissionInProgress.current = false;
      setSubmitting(false);
    }
  }

  return (
    <section className="create-panel edit-panel" aria-labelledby="faculty-edit-heading">
      <div className="section-heading">
        <div>
          <h3 id="faculty-edit-heading">Edit faculty member</h3>
          <p className="muted">Department ownership cannot be changed here.</p>
        </div>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Name
            <input
              name="name"
              value={values.name}
              onChange={updateValue}
              disabled={submitting}
              required
            />
          </label>
          <label>
            Title
            <input
              name="title"
              value={values.title}
              onChange={updateValue}
              disabled={submitting}
            />
          </label>
          <label>
            Contact information
            <input
              name="contact_information"
              value={values.contact_information}
              onChange={updateValue}
              disabled={submitting}
            />
          </label>
          <label>
            Profile image reference
            <input
              name="profile_image_reference"
              value={values.profile_image_reference}
              onChange={updateValue}
              disabled={submitting}
            />
          </label>
        </div>
        <label>
          Biography
          <textarea
            name="biography"
            value={values.biography}
            onChange={updateValue}
            disabled={submitting}
            rows="3"
          />
        </label>
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
        {success && (
          <p className="form-success" role="status">
            {success}
          </p>
        )}
        <div className="form-actions">
          <button type="submit" disabled={submitting}>
            {submitting ? "Saving…" : "Save changes"}
          </button>
          <button
            className="secondary"
            type="button"
            onClick={onCancel}
            disabled={submitting}
          >
            Cancel
          </button>
        </div>
      </form>
    </section>
  );
}
