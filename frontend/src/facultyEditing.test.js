import assert from "node:assert/strict";
import test from "node:test";
import {
  canEditFaculty,
  facultyEditValues,
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

test("only super administrators can edit faculty", () => {
  assert.equal(canEditFaculty("super_admin"), true);
  assert.equal(canEditFaculty("department_admin"), false);
  assert.equal(canEditFaculty("unknown"), false);
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
