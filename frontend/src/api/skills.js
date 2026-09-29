import { apiFetch } from "./client";

export function getEmployeeSkillProfile(idEmployee) {
  return apiFetch(`/employees/${idEmployee}/skills`);
}

export function getAllSkills() {
  return apiFetch("/skill");
}

export function getValidationTypes() {
  return apiFetch("/validation_type");
}

export function createSkillValidation(payload) {
  return apiFetch("/skill_validation", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getSkillValidationHistory(idEmployee, idSkill) {
  return apiFetch(`/skill_validation/employees/${idEmployee}/skills/${idSkill}/history`);
}
