import assert from "node:assert/strict";
import test from "node:test";
import { AxiosError } from "axios";
import { createAuthenticatedClient } from "./api.js";
import { AuthorizationError, createAuthService } from "./auth.js";

function response(config, data, status = 200) {
  return { data, status, statusText: "OK", headers: {}, config };
}

function rejectedResponse(config, status) {
  return Promise.reject(
    new AxiosError(
      "Request failed",
      AxiosError.ERR_BAD_RESPONSE,
      config,
      null,
      response(config, {}, status),
    ),
  );
}

function sessionPayload(overrides = {}) {
  return {
    user: {
      id: "user-1",
      email: "admin@example.invalid",
      role: "super_admin",
      is_active: true,
      ...overrides,
    },
    csrf_token: "csrf-test-token",
  };
}

function setup(adapter) {
  const session = createAuthenticatedClient({ baseURL: "http://test.invalid" });
  session.client.defaults.adapter = adapter;
  return { session, auth: createAuthService(session) };
}

test("login creates a cookie session without storing a bearer token", async () => {
  const requests = [];
  const { session, auth } = setup(async (config) => {
    requests.push(config);
    return response(config, sessionPayload());
  });

  const user = await auth.login("admin@example.invalid", "secret password");

  assert.equal(user.role, "super_admin");
  assert.equal(requests.length, 1);
  assert.equal(requests[0].url, "/auth/session/login");
  assert.equal(
    requests[0].data,
    "username=admin%40example.invalid&password=secret+password",
  );
  assert.match(
    requests[0].headers.get("Content-Type"),
    /^application\/x-www-form-urlencoded/,
  );
  assert.equal(requests[0].withCredentials, true);
  assert.equal(session.hasAccessToken(), false);
  assert.equal(session.hasSession(), true);
});

test("refresh restoration validates the current persistent session", async () => {
  const { session, auth } = setup(async (config) => {
    assert.equal(config.url, "/auth/session");
    assert.equal(config.withCredentials, true);
    return response(config, sessionPayload({ role: "department_admin" }));
  });

  const user = await auth.restore();
  assert.equal(user.role, "department_admin");
  assert.equal(session.hasSession(), true);
});

test("invalid credentials do not create a session", async () => {
  const { session, auth } = setup((config) => rejectedResponse(config, 401));
  await assert.rejects(auth.login("admin@example.invalid", "wrong"));
  assert.equal(session.hasSession(), false);
});

test("session responses reject inactive and non-administrator accounts", async (t) => {
  for (const user of [
    { role: "student", is_active: true },
    { role: "super_admin", is_active: false },
  ]) {
    await t.test(`${user.role}:${user.is_active}`, async () => {
      const { session, auth } = setup(async (config) =>
        response(config, sessionPayload(user)),
      );
      await assert.rejects(
        auth.login("user@example.invalid", "password"),
        AuthorizationError,
      );
      assert.equal(session.hasSession(), false);
    });
  }
});

test("unsafe cookie requests attach CSRF and logout clears the session", async () => {
  const requests = [];
  const { session, auth } = setup(async (config) => {
    requests.push(config);
    return response(config, {});
  });
  session.setCsrfToken("memory-csrf-token");

  await session.client.get("/departments/");
  await session.client.post("/faculty_members/", {});
  await auth.logout();

  assert.equal(requests[0].headers.get("X-CSRF-Token"), undefined);
  assert.equal(requests[1].headers.get("X-CSRF-Token"), "memory-csrf-token");
  assert.equal(requests[2].url, "/auth/session/logout");
  assert.equal(requests[2].headers.get("X-CSRF-Token"), "memory-csrf-token");
  assert.equal(session.hasSession(), false);
});

test("401 invalidates the session while 403 preserves it", async () => {
  let status = 403;
  let unauthorizedCalls = 0;
  const { session } = setup((config) => rejectedResponse(config, status));
  session.setUnauthorizedHandler(() => {
    unauthorizedCalls += 1;
  });
  session.setCsrfToken("memory-csrf-token");
  await assert.rejects(session.client.get("/forbidden"));
  assert.equal(session.hasSession(), true);
  assert.equal(unauthorizedCalls, 0);
  status = 401;
  await assert.rejects(session.client.get("/expired"));
  assert.equal(session.hasSession(), false);
  assert.equal(unauthorizedCalls, 1);
});

test("an explicit bearer token takes precedence over cookie CSRF", async () => {
  const { session } = setup(async (config) => {
    assert.equal(config.headers.get("Authorization"), "Bearer api-token");
    assert.equal(config.headers.get("X-CSRF-Token"), undefined);
    return response(config, {});
  });
  session.setCsrfToken("memory-csrf-token");
  session.setAccessToken("api-token");
  await session.client.post("/faculty_members/", {});
});

test("authentication never uses browser storage", async () => {
  let storageCalls = 0;
  const originalLocalStorage = globalThis.localStorage;
  const originalSessionStorage = globalThis.sessionStorage;
  const storage = new Proxy({}, {
    get() {
      storageCalls += 1;
      return () => {
        storageCalls += 1;
      };
    },
  });
  globalThis.localStorage = storage;
  globalThis.sessionStorage = storage;
  try {
    const { auth } = setup(async (config) =>
      response(config, sessionPayload()),
    );
    await auth.login("admin@example.invalid", "password");
    await auth.restore();
    await auth.logout();
    assert.equal(storageCalls, 0);
  } finally {
    if (originalLocalStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = originalLocalStorage;
    if (originalSessionStorage === undefined) delete globalThis.sessionStorage;
    else globalThis.sessionStorage = originalSessionStorage;
  }
});
