import { apiFetch } from "./client";

export function getAvailableTrainings(idEmployee, idDomaine) {
  const query = idDomaine ? `?id_domaine=${encodeURIComponent(idDomaine)}` : "";
  return apiFetch(`/employees/${idEmployee}/available-trainings${query}`);
}

export function getTrainings() {
  return apiFetch("/training");
}
