import { apiFetch } from "./client";

export function getEmployeeSkillProfile(idEmployee) {
  return apiFetch(`/employees/${idEmployee}/skills`);
}
