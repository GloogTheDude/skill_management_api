import { apiFetch } from "./client";

export function getDomaines() { return apiFetch("/domaine"); }
export function getTrainingSources() { return apiFetch("/training_source"); }
export function getSkills() { return apiFetch("/skill"); }
export function getDiplomas() { return apiFetch("/diploma"); }
export function getCertifications() { return apiFetch("/certification"); }
export function getValidationTypes() { return apiFetch("/validation_type"); }

export function createDomaine(body) { return apiFetch("/domaine", { method: "POST", body: JSON.stringify(body) }); }
export function updateDomaine(id, body) { return apiFetch(`/domaine/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveDomaine(id) { return apiFetch(`/domaine/${id}`, { method: "DELETE" }); }
export function createTrainingSource(body) { return apiFetch("/training_source", { method: "POST", body: JSON.stringify(body) }); }
export function updateTrainingSource(id, body) { return apiFetch(`/training_source/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveTrainingSource(id) { return apiFetch(`/training_source/${id}`, { method: "DELETE" }); }
export function createSkill(body) { return apiFetch("/skill", { method: "POST", body: JSON.stringify(body) }); }
export function updateSkill(id, body) { return apiFetch(`/skill/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveSkill(id) { return apiFetch(`/skill/${id}`, { method: "DELETE" }); }
export function createDiploma(body) { return apiFetch("/diploma", { method: "POST", body: JSON.stringify(body) }); }
export function updateDiploma(id, body) { return apiFetch(`/diploma/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveDiploma(id) { return apiFetch(`/diploma/${id}`, { method: "DELETE" }); }
export function createCertification(body) { return apiFetch("/certification", { method: "POST", body: JSON.stringify(body) }); }
export function updateCertification(id, body) { return apiFetch(`/certification/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveCertification(id) { return apiFetch(`/certification/${id}`, { method: "DELETE" }); }
export function createValidationType(body) { return apiFetch("/validation_type", { method: "POST", body: JSON.stringify(body) }); }
export function updateValidationType(id, body) { return apiFetch(`/validation_type/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function archiveValidationType(id) { return apiFetch(`/validation_type/${id}`, { method: "DELETE" }); }
export function getDiplomaSkills() { return apiFetch("/diploma_skill"); }
export function getCertificationSkills() { return apiFetch("/certification_skill"); }
export function replaceDiplomaSkills(id, skills) { return apiFetch(`/diploma/s/${id}/skills`, { method: "PUT", body: JSON.stringify({ skills }) }); }
export function replaceCertificationSkills(id, skills) { return apiFetch(`/certification/s/${id}/skills`, { method: "PUT", body: JSON.stringify({ skills }) }); }
