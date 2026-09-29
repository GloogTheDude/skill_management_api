import { apiFetch } from "./client";

export function getParticipations() {
  return apiFetch("/participations");
}

export function getCompletableParticipations() {
  return apiFetch("/participations/completable");
}

export function startParticipation(idEmployee, idTraining) {
  return apiFetch(`/participations/${idEmployee}/${idTraining}/start`, {
    method: "POST",
  });
}

export function completeParticipation(idEmployee, idTraining) {
  return apiFetch(`/participations/${idEmployee}/${idTraining}/complete`, {
    method: "POST",
  });
}
