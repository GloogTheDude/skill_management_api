import { apiFetch } from "./client";

export function getAvailableTrainings(idEmployee, idDomaine) {
  const query = idDomaine ? `?id_domaine=${encodeURIComponent(idDomaine)}` : "";
  return apiFetch(`/employees/${idEmployee}/available-trainings${query}`);
}

export function getTrainings() {
  return apiFetch("/training");
}

export function createTraining(payload) {
  return apiFetch("/training", { method: "POST", body: JSON.stringify(payload) });
}

export function updateTraining(idTraining, payload) {
  return apiFetch(`/training/${idTraining}`, { method: "PATCH", body: JSON.stringify(payload) });
}

export function archiveTraining(idTraining) {
  return apiFetch(`/training/${idTraining}`, { method: "DELETE" });
}

export function getTrainingSkills() {
  return apiFetch("/training_skill");
}
