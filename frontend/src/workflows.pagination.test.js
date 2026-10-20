import assert from "node:assert/strict";
import test from "node:test";

import { loadAdministrativeData } from "./workflows.js";

function records(prefix, count) {
  return Array.from({ length: count }, (_, index) => ({
    id: `${prefix}-${index}`,
  }));
}

function paginatedApi(data) {
  const requests = [];
  return {
    requests,
    api: {
      async get(path, { params }) {
        requests.push({ path, ...params });
        return {
          data: data[path].slice(params.skip, params.skip + params.limit),
        };
      },
    },
  };
}

test("super administrator loads every department, faculty, and college page", async () => {
  const data = {
    "/departments/": records("department", 205),
    "/faculty_members/": records("faculty", 101),
    "/colleges/": records("college", 200),
  };
  const { api, requests } = paginatedApi(data);

  const result = await loadAdministrativeData(api, "super_admin");

  assert.deepEqual(result, {
    departments: data["/departments/"],
    faculty: data["/faculty_members/"],
    colleges: data["/colleges/"],
  });
  for (const [path, skips] of [
    ["/departments/", [0, 100, 200]],
    ["/faculty_members/", [0, 100]],
    ["/colleges/", [0, 100, 200]],
  ]) {
    assert.deepEqual(
      requests.filter((request) => request.path === path).map(({ skip, limit }) => ({ skip, limit })),
      skips.map((skip) => ({ skip, limit: 100 })),
    );
  }
});

test("department administrator loads scoped lists only, including additional pages", async () => {
  const data = {
    "/departments/": records("department", 101),
    "/faculty_members/": records("faculty", 201),
  };
  const { api, requests } = paginatedApi(data);

  const result = await loadAdministrativeData(api, "department_admin");

  assert.deepEqual(result.departments, data["/departments/"]);
  assert.deepEqual(result.faculty, data["/faculty_members/"]);
  assert.deepEqual(result.colleges, []);
  assert.equal(requests.some((request) => request.path === "/colleges/"), false);
});

test("a broken API repeating a full page fails instead of looping or returning duplicates", async () => {
  const fullPage = records("faculty", 100);
  const api = {
    async get(path) {
      return { data: path === "/faculty_members/" ? fullPage : [] };
    },
  };

  await assert.rejects(
    loadAdministrativeData(api, "department_admin"),
    /Repeated or invalid list record/,
  );
});

test("list request failures are propagated without returning partial data", async () => {
  const api = {
    async get(path, { params }) {
      if (path === "/faculty_members/" && params.skip === 100) {
        throw Object.assign(new Error("unauthorized"), { response: { status: 403 } });
      }
      return { data: path === "/faculty_members/" ? records("faculty", 100) : [] };
    },
  };

  await assert.rejects(
    loadAdministrativeData(api, "department_admin"),
    (error) => error.response?.status === 403,
  );
});
