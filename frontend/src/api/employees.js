import { apiFetch } from "./client";

export function getEmployees() { return apiFetch("/employee"); }
export function getRoles() { return apiFetch("/role"); }
export function getAccessLevels() { return apiFetch("/access_level"); }
export function createEmployee(body) { return apiFetch("/employee", { method: "POST", body: JSON.stringify(body) }); }
export function updateEmployee(id, body) { return apiFetch(`/employee/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveEmployee(id) { return apiFetch(`/employee/${id}`, { method: "DELETE" }); }
