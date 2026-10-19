import test from "node:test";
import assert from "node:assert/strict";

import { updateFacultyMember } from "./workflows.js";

test("updateFacultyMember sends permitted fields and returns response data", async () => {
  const calls = [];
  const updatedFaculty = {
    id: "faculty-1",
    department_id: "department-1",
    name: "Updated Name",
  };
  const api = {
    async put(path, payload) {
      calls.push({ path, payload });
      return { data: updatedFaculty };
    },
  };
  const values = {
    name: "Updated Name",
    title: "Professor",
    biography: "Updated biography",
    contact_information: "faculty@example.invalid",
    profile_image_reference: "faculty/profile.webp",
  };

  const result = await updateFacultyMember(api, "faculty-1", values);

  assert.strictEqual(result, updatedFaculty);
  assert.deepEqual(calls, [
    {
      path: "/faculty_members/faculty-1",
      payload: values,
    },
  ]);
});

test("updateFacultyMember excludes protected and unexpected fields", async () => {
  let receivedPath;
  let receivedPayload;
  const api = {
    async put(path, payload) {
      receivedPath = path;
      receivedPayload = payload;
      return { data: { id: "faculty/1", ...payload } };
    },
  };

  await updateFacultyMember(api, "faculty/1", {
    name: "Permitted Name",
    department_id: "unauthorized-department",
    id: "replacement-id",
    created_at: "2026-10-17T00:00:00Z",
    updated_at: "2026-10-17T00:00:00Z",
    deleted_at: "2026-10-17T00:00:00Z",
    ownership: "unauthorized",
    unexpected: "unauthorized",
  });

  assert.equal(receivedPath, "/faculty_members/faculty%2F1");
  assert.deepEqual(receivedPayload, {
    name: "Permitted Name",
  });
});
