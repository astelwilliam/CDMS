import { requestErrorMessage } from "./workflows.js";

const EDITABLE_FACULTY_FIELDS = [
  "name",
  "title",
  "biography",
  "contact_information",
  "profile_image_reference",
];

export function facultyEditValues(facultyMember) {
  return Object.fromEntries(
    EDITABLE_FACULTY_FIELDS.map((field) => [field, facultyMember[field] ?? ""]),
  );
}

export function replaceFacultyMember(faculty, updatedFacultyMember) {
  return faculty.map((facultyMember) =>
    facultyMember.id === updatedFacultyMember.id
      ? updatedFacultyMember
      : facultyMember,
  );
}

export function refreshEditingFaculty(selection, updatedFacultyMember) {
  return selection?.id === updatedFacultyMember.id
    ? updatedFacultyMember
    : selection;
}

export function facultyRecordStatuses(facultyMember, departments) {
  const statuses = [];
  if (facultyMember?.deleted_at === undefined) {
    statuses.push("Read-only — Faculty status unavailable");
  } else if (facultyMember.deleted_at !== null) {
    statuses.push("Deleted");
  }

  const department = departments.find(
    (item) => item.id === facultyMember?.department_id,
  );
  if (!department || department.deleted_at === undefined) {
    statuses.push("Read-only — Department unavailable");
  } else if (department.deleted_at !== null) {
    statuses.push("Read-only — Department deleted");
  }

  return statuses;
}

export function canEditFaculty(role, facultyMember, departments) {
  return (
    role === "super_admin" &&
    facultyRecordStatuses(facultyMember, departments).length === 0
  );
}

export function editableFacultySelection(selection, faculty, departments, role) {
  if (!selection) return null;
  const current = faculty.find((member) => member.id === selection.id);
  return canEditFaculty(role, current, departments) ? current : null;
}

export function facultyUpdateErrorMessage(error) {
  if (error?.response?.status === 404) {
    return "This faculty member is no longer available.";
  }
  return requestErrorMessage(error) || "";
}
