import { apiFetch } from "./client";

export function login(mail, password) {
  return apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ mail, password }),
  });
}

export function getCurrentUser() {
  return apiFetch("/auth/me");
}

export function logout() {
  return apiFetch("/auth/logout", { method: "POST" });
}
