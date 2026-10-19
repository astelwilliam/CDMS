export function departmentEmptyMessage(role) {
  return role === "department_admin"
    ? "No assigned departments found."
    : "No departments found.";
}
