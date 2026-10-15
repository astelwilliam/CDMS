import { apiSession } from "./api.js";

const administratorRoles = new Set(["super_admin", "department_admin"]);

export class AuthorizationError extends Error {
  constructor(message = "This account is not authorized for administration.") {
    super(message);
    this.name = "AuthorizationError";
  }
}

export function createAuthService(session = apiSession) {
  function acceptSession(data) {
    const { user, csrf_token: csrfToken } = data || {};
    if (!csrfToken || !user?.is_active || !administratorRoles.has(user.role)) {
      throw new AuthorizationError();
    }
    session.setCsrfToken(csrfToken);
    return user;
  }

  return {
    async login(email, password) {
      const credentials = new URLSearchParams({ username: email, password });

      try {
        const loginResponse = await session.client.post(
          "/auth/session/login",
          credentials,
          {
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
          },
        );
        return acceptSession(loginResponse.data);
      } catch (error) {
        session.clearAuthentication();
        throw error;
      }
    },
    async restore() {
      try {
        const response = await session.client.get("/auth/session");
        return acceptSession(response.data);
      } catch (error) {
        session.clearAuthentication();
        throw error;
      }
    },
    async logout() {
      try {
        if (session.hasSession()) {
          await session.client.post("/auth/session/logout");
        }
      } finally {
        session.clearAuthentication();
      }
    },
    onUnauthorized(handler) {
      session.setUnauthorizedHandler(handler);
    },
  };
}

export const authService = createAuthService();
