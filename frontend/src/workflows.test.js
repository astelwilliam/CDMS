import assert from "node:assert/strict";
import test from "node:test";
import {
  createFacultyMember,
  loadAdministrativeData,
  requestErrorMessage,
} from "./workflows.js";

function apiFixture() {
  const requests = [];
  return {
    requests,
    api: {
      async get(url, config) {
        requests.push({ method: "GET", url, config });
        const data = {
          "/departments/": [{ id: "department-1", name: "Computing" }],
          "/faculty_members/": [{ id: "faculty-1", name: "Professor" }],
          "/colleges/": [{ id: "college-1", name: "Engineering" }],
        }[url];
        return { data };
      },
      async post(url, data) {
        requests.push({ method: "POST", url, data });
        return { data: { id: "faculty-2", ...data } };
      },
    },
  };
}

test("super administrators load colleges, departments, and faculty", async () => {
  const fixture = apiFixture();
  const result = await loadAdministrativeData(fixture.api, "super_admin");

  assert.equal(result.colleges.length, 1);
  assert.equal(result.departments.length, 1);
  assert.equal(result.faculty.length, 1);
  assert.deepEqual(
    fixture.requests.map(({ method, url }) => `${method} ${url}`),
    ["GET /departments/", "GET /faculty_members/", "GET /colleges/"],
  );
  assert.deepEqual(fixture.requests[0].config.params, { skip: 0, limit: 100 });
});

test("department administrators request only scoped department and faculty APIs", async () => {
  const fixture = apiFixture();
  const result = await loadAdministrativeData(fixture.api, "department_admin");

  assert.deepEqual(result.colleges, []);
  assert.deepEqual(
    fixture.requests.map(({ method, url }) => `${method} ${url}`),
    ["GET /departments/", "GET /faculty_members/"],
  );
});

test("faculty creation sends only the supplied API fields", async () => {
  const fixture = apiFixture();
  const payload = {
    name: "New Member",
    title: "Lecturer",
    biography: "",
    contact_information: "contact@example.invalid",
    profile_image_reference: "",
    department_id: "department-1",
  };

  const result = await createFacultyMember(fixture.api, payload);

  assert.equal(result.id, "faculty-2");
  assert.deepEqual(fixture.requests, [
    { method: "POST", url: "/faculty_members/", data: payload },
  ]);
});

test("request errors distinguish authentication and authorization", () => {
  assert.equal(requestErrorMessage({ response: { status: 401 } }), "");
  assert.equal(
    requestErrorMessage({ response: { status: 403 } }),
    "Your account is not authorized for this action.",
  );
  assert.equal(
    requestErrorMessage({ response: { status: 404 } }),
    "The selected department is unavailable.",
  );
  assert.equal(
    requestErrorMessage({ response: { status: 503 } }),
    "The service is temporarily unavailable. Try again.",
  );
});
