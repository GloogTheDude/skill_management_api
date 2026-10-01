import { apiFetch } from "./client";

export function getEmployeeDeclaredSkills(idEmployee) { return apiFetch(`/employee_declared_skill/employee/${idEmployee}`); }
export function createEmployeeDeclaredSkill(body) { return apiFetch("/employee_declared_skill", { method: "POST", body: JSON.stringify(body) }); }
export function updateEmployeeDeclaredSkill(id, body) { return apiFetch(`/employee_declared_skill/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveEmployeeDeclaredSkill(id) { return apiFetch(`/employee_declared_skill/${id}`, { method: "DELETE" }); }
