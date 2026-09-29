import { apiFetch } from "./client";

export function getEmployees() { return apiFetch("/employee"); }
export function getRoles() { return apiFetch("/role"); }
export function getAccessLevels() { return apiFetch("/access_level"); }
export function createEmployee(body) { return apiFetch("/employee", { method: "POST", body: JSON.stringify(body) }); }
export function updateEmployee(id, body) { return apiFetch(`/employee/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveEmployee(id) { return apiFetch(`/employee/${id}`, { method: "DELETE" }); }
export function getEmployeeDiplomas(id) { return apiFetch(`/employee_diploma/employee/${id}`); }
export function createEmployeeDiploma(body) { return apiFetch("/employee_diploma", { method: "POST", body: JSON.stringify(body) }); }
export function updateEmployeeDiploma(employeeId, diplomaId, body) { return apiFetch(`/employee_diploma/${employeeId}/${diplomaId}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveEmployeeDiploma(employeeId, diplomaId) { return apiFetch(`/employee_diploma/${employeeId}/${diplomaId}`, { method: "DELETE" }); }
export function getEmployeeCertifications(id) { return apiFetch(`/employee_certification/employee/${id}`); }
export function createEmployeeCertification(body) { return apiFetch("/employee_certification", { method: "POST", body: JSON.stringify(body) }); }
export function updateEmployeeCertification(id, body) { return apiFetch(`/employee_certification/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveEmployeeCertification(id) { return apiFetch(`/employee_certification/${id}`, { method: "DELETE" }); }
