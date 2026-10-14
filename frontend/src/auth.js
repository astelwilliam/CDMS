import { apiSession } from "./api.js";

const administratorRoles = new Set(["super_admin", "department_admin"]);

export class AuthorizationError extends Error {
  constructor(message = "This account is not authorized for administration.") {
    super(message);
    this.name = "AuthorizationError";
  }
}

export function createAuthService(session = apiSession) {
  return {
    async login(email, password) {
      const credentials = new URLSearchParams({ username: email, password });

      try {
        const loginResponse = await session.client.post(
          "/auth/login",
          credentials,
          {
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
          },
        );
        const { access_token: accessToken, token_type: tokenType } =
          loginResponse.data;

        if (!accessToken || tokenType?.toLowerCase() !== "bearer") {
          throw new Error("The authentication response was invalid.");
        }

        session.setAccessToken(accessToken);
        const profileResponse = await session.client.get("/auth/me");
        const user = profileResponse.data;

        if (!user?.is_active || !administratorRoles.has(user.role)) {
          throw new AuthorizationError();
        }

        return user;
      } catch (error) {
        session.clearAccessToken();
        throw error;
      }
    },
    logout() {
      session.clearAccessToken();
    },
    onUnauthorized(handler) {
      session.setUnauthorizedHandler(handler);
    },
  };
}

export const authService = createAuthService();
