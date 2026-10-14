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

function setup(adapter) {
  const session = createAuthenticatedClient({ baseURL: "http://test.invalid" });
  session.client.defaults.adapter = adapter;
  return { session, auth: createAuthService(session) };
}

test("login posts form credentials, validates /auth/me, and keeps token in memory", async () => {
  const requests = [];
  const { session, auth } = setup(async (config) => {
    requests.push(config);
    if (config.url === "/auth/login") {
      return response(config, {
        access_token: "test-token",
        token_type: "bearer",
      });
    }
    return response(config, {
      id: "user-1",
      email: "admin@example.invalid",
      role: "super_admin",
      is_active: true,
    });
  });

  const user = await auth.login("admin@example.invalid", "secret password");

  assert.equal(user.role, "super_admin");
  assert.equal(requests.length, 2);
  assert.equal(requests[0].data, "username=admin%40example.invalid&password=secret+password");
  assert.match(requests[0].headers.get("Content-Type"), /^application\/x-www-form-urlencoded/);
  assert.equal(requests[1].headers.get("Authorization"), "Bearer test-token");
  assert.equal(session.hasAccessToken(), true);
});

test("invalid credentials do not create a session", async () => {
  const { session, auth } = setup((config) => rejectedResponse(config, 401));
  await assert.rejects(auth.login("admin@example.invalid", "wrong"));
  assert.equal(session.hasAccessToken(), false);
});

test("/auth/me rejects inactive and non-administrator accounts", async (t) => {
  for (const user of [
    { role: "student", is_active: true },
    { role: "super_admin", is_active: false },
  ]) {
    await t.test(`${user.role}:${user.is_active}`, async () => {
      const { session, auth } = setup(async (config) =>
        config.url === "/auth/login"
          ? response(config, { access_token: "token", token_type: "bearer" })
          : response(config, {
              id: "user-1",
              email: "user@example.invalid",
              ...user,
            }),
      );
      await assert.rejects(
        auth.login("user@example.invalid", "password"),
        AuthorizationError,
      );
      assert.equal(session.hasAccessToken(), false);
    });
  }
});

test("authenticated requests attach bearer credentials and logout removes them", async () => {
  const authorizations = [];
  const { session, auth } = setup(async (config) => {
    authorizations.push(config.headers.get("Authorization"));
    return response(config, {});
  });
  session.setAccessToken("memory-token");
  await session.client.get("/departments/");
  auth.logout();
  await session.client.get("/departments/");
  assert.deepEqual(authorizations, ["Bearer memory-token", undefined]);
  assert.equal(session.hasAccessToken(), false);
});

test("401 invalidates the session while 403 preserves it", async () => {
  let status = 403;
  let unauthorizedCalls = 0;
  const { session } = setup((config) => rejectedResponse(config, status));
  session.setUnauthorizedHandler(() => {
    unauthorizedCalls += 1;
  });
  session.setAccessToken("memory-token");
  await assert.rejects(session.client.get("/forbidden"));
  assert.equal(session.hasAccessToken(), true);
  assert.equal(unauthorizedCalls, 0);
  status = 401;
  await assert.rejects(session.client.get("/expired"));
  assert.equal(session.hasAccessToken(), false);
  assert.equal(unauthorizedCalls, 1);
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
      config.url === "/auth/login"
        ? response(config, { access_token: "token", token_type: "bearer" })
        : response(config, {
            id: "user-1",
            email: "admin@example.invalid",
            role: "department_admin",
            is_active: true,
          }),
    );
    await auth.login("admin@example.invalid", "password");
    auth.logout();
    assert.equal(storageCalls, 0);
  } finally {
    if (originalLocalStorage === undefined) delete globalThis.localStorage;
    else globalThis.localStorage = originalLocalStorage;
    if (originalSessionStorage === undefined) delete globalThis.sessionStorage;
    else globalThis.sessionStorage = originalSessionStorage;
  }
});
