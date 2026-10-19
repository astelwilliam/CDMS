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

export function canEditFaculty(role) {
  return role === "super_admin";
}

export function facultyUpdateErrorMessage(error) {
  if (error?.response?.status === 404) {
    return "This faculty member is no longer available.";
  }
  return requestErrorMessage(error) || "";
}
