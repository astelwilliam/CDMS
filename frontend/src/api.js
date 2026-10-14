import axios from "axios";

const defaultBaseURL =
  import.meta.env?.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export function createAuthenticatedClient(options = {}) {
  const client = axios.create({
    baseURL: options.baseURL || defaultBaseURL,
    timeout: options.timeout || 5000,
  });
  let accessToken = null;
  let unauthorizedHandler = null;

  client.interceptors.request.use((config) => {
    if (accessToken) {
      config.headers.set("Authorization", `Bearer ${accessToken}`);
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401 && accessToken) {
        accessToken = null;
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
    hasAccessToken() {
      return Boolean(accessToken);
    },
    setUnauthorizedHandler(handler) {
      unauthorizedHandler = handler;
    },
  };
}

export const apiSession = createAuthenticatedClient();

export default apiSession.client;
