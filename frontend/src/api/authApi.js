import { request } from "./httpClient.js";

export const authApi = {
  login: (username, password) =>
    request("/auth/login", { method: "POST", body: { username, password }, auth: false }),
  me: () => request("/auth/me"),
};

export const dashboardApi = {
  summary: () => request("/dashboard/summary"),
  users: () => request("/admin/users"),
};
