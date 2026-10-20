import assert from "node:assert/strict";
import test from "node:test";
import {
  canEditFaculty,
  editableFacultySelection,
  facultyEditValues,
  facultyRecordStatuses,
  facultyUpdateErrorMessage,
  refreshEditingFaculty,
  replaceFacultyMember,
} from "./facultyEditing.js";

test("faculty edit values include only editable fields", () => {
  assert.deepEqual(
    facultyEditValues({
      id: "faculty-1",
      department_id: "department-1",
      name: "Professor Example",
      title: null,
      biography: "Biography",
      contact_information: "contact@example.invalid",
      profile_image_reference: null,
      deleted_at: null,
    }),
    {
      name: "Professor Example",
      title: "",
      biography: "Biography",
      contact_information: "contact@example.invalid",
      profile_image_reference: "",
    },
  );
});

test("a successful edit replaces only the matching faculty record", () => {
  const existing = [
    { id: "faculty-1", name: "Original" },
    { id: "faculty-2", name: "Unchanged" },
  ];
  const updated = { id: "faculty-1", name: "Updated" };

  assert.deepEqual(replaceFacultyMember(existing, updated), [
    updated,
    existing[1],
  ]);
  assert.equal(existing[0].name, "Original");
});

test("a pending save leaves a newer editor selection untouched", async () => {
  const original = { id: "faculty-1", name: "Original" };
  const other = { id: "faculty-2", name: "Other" };
  const updated = { id: "faculty-1", name: "Updated" };
  let selection = original;
  let completeSave;
  const pendingSave = new Promise((resolve) => {
    completeSave = resolve;
  }).then((response) => {
    selection = refreshEditingFaculty(selection, response);
  });

  selection = other;
  completeSave(updated);
  await pendingSave;
  assert.equal(selection, other);

  selection = null;
  assert.equal(refreshEditingFaculty(selection, updated), null);
  assert.equal(refreshEditingFaculty(original, updated), updated);
});

test("only active faculty in confirmed active departments are editable by super administrators", () => {
  const active = { id: "faculty-1", department_id: "department-1", deleted_at: null };
  const departments = [
    { id: "department-1", deleted_at: null },
    { id: "department-2", deleted_at: "2026-10-20T12:00:00Z" },
  ];

  assert.equal(canEditFaculty("super_admin", active, departments), true);
  assert.equal(canEditFaculty("department_admin", active, departments), false);
  assert.equal(canEditFaculty("unknown", active, departments), false);
  assert.equal(canEditFaculty("super_admin", { ...active, deleted_at: "2026-10-20T12:00:00Z" }, departments), false);
  assert.equal(canEditFaculty("super_admin", { ...active, department_id: "department-2" }, departments), false);
  assert.equal(canEditFaculty("super_admin", { ...active, department_id: "missing" }, departments), false);
  assert.equal(canEditFaculty("super_admin", { id: "faculty-1", department_id: "department-1" }, departments), false);
  assert.equal(canEditFaculty("super_admin", active, [{ id: "department-1" }]), false);
});

test("historical faculty status distinguishes deletion and unavailable departments", () => {
  const active = { id: "faculty-1", department_id: "department-1", deleted_at: null };
  const departments = [
    { id: "department-1", deleted_at: null },
    { id: "department-2", deleted_at: "2026-10-20T12:00:00Z" },
  ];

  assert.deepEqual(facultyRecordStatuses(active, departments), []);
  assert.deepEqual(facultyRecordStatuses({ ...active, deleted_at: "2026-10-20T12:00:00Z" }, departments), ["Deleted"]);
  assert.deepEqual(facultyRecordStatuses({ ...active, department_id: "department-2" }, departments), ["Read-only — Department deleted"]);
  assert.deepEqual(facultyRecordStatuses({ ...active, department_id: "missing" }, departments), ["Read-only — Department unavailable"]);
  assert.deepEqual(facultyRecordStatuses({ id: "faculty-1", department_id: "department-1" }, departments), ["Read-only — Faculty status unavailable"]);
});

test("a refreshed faculty record closes an editor when editing is no longer allowed", () => {
  const selected = { id: "faculty-1", department_id: "department-1", deleted_at: null };
  const other = { id: "faculty-2", department_id: "department-1", deleted_at: null };
  const activeDepartments = [{ id: "department-1", deleted_at: null }];

  assert.equal(editableFacultySelection(selected, [selected, other], activeDepartments, "super_admin"), selected);
  assert.equal(editableFacultySelection(selected, [other], activeDepartments, "super_admin"), null);
  assert.equal(editableFacultySelection(selected, [{ ...selected, deleted_at: "2026-10-20T12:00:00Z" }], activeDepartments, "super_admin"), null);
  assert.equal(editableFacultySelection(selected, [selected], [{ id: "department-1", deleted_at: "2026-10-20T12:00:00Z" }], "super_admin"), null);
  assert.equal(editableFacultySelection(selected, [selected], [], "super_admin"), null);
  assert.equal(editableFacultySelection(selected, [selected], activeDepartments, "department_admin"), null);
  assert.equal(editableFacultySelection(selected, [other, { ...selected, name: "Refreshed" }], activeDepartments, "super_admin")?.name, "Refreshed");
});

test("faculty update errors distinguish unavailable records and permissions", () => {
  assert.equal(
    facultyUpdateErrorMessage({ response: { status: 404 } }),
    "This faculty member is no longer available.",
  );
  assert.equal(
    facultyUpdateErrorMessage({ response: { status: 403 } }),
    "Your account is not authorized for this action.",
  );
  assert.equal(
    facultyUpdateErrorMessage({ response: { status: 503 } }),
    "The service is temporarily unavailable. Try again.",
  );
  assert.equal(facultyUpdateErrorMessage({ response: { status: 401 } }), "");
});
