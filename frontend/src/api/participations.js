import { apiFetch } from "./client";

export function getParticipations() {
  return apiFetch("/participations");
}

export function getCompletableParticipations() {
  return apiFetch("/participations/completable");
}

export function closeParticipation(idEmployee, idTraining, result) {
  return apiFetch(`/participations/${idEmployee}/${idTraining}/close`, {
    method: "POST",
    body: JSON.stringify({ result }),
  });
}
