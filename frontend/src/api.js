import axios from "axios";

const defaultBaseURL =
  import.meta.env?.VITE_API_BASE_URL || "http://localhost:8000";

const unsafeMethods = new Set(["POST", "PUT", "PATCH", "DELETE"]);

export function createAuthenticatedClient(options = {}) {
  const client = axios.create({
    baseURL: options.baseURL || defaultBaseURL,
    timeout: options.timeout || 5000,
    withCredentials: true,
  });
  let accessToken = null;
  let csrfToken = null;
  let unauthorizedHandler = null;

  client.interceptors.request.use((config) => {
    if (accessToken) {
      config.headers.set("Authorization", `Bearer ${accessToken}`);
    } else if (csrfToken && unsafeMethods.has(config.method?.toUpperCase())) {
      config.headers.set("X-CSRF-Token", csrfToken);
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401 && (accessToken || csrfToken)) {
        accessToken = null;
        csrfToken = null;
        unauthorizedHandler?.();
      }
      return Promise.reject(error);
    },
  );

  return {
    client,
    setAccessToken(token) {
      accessToken = token;
    },
    clearAccessToken() {
      accessToken = null;
    },
    setCsrfToken(token) {
      csrfToken = token;
    },
    clearAuthentication() {
      accessToken = null;
      csrfToken = null;
    },
    hasAccessToken() {
      return Boolean(accessToken);
    },
    hasSession() {
      return Boolean(csrfToken);
    },
    setUnauthorizedHandler(handler) {
      unauthorizedHandler = handler;
    },
  };
}

export const apiSession = createAuthenticatedClient();

export default apiSession.client;
