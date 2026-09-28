import { apiFetch } from "./client";

export function getMyTrainingRequests() {
  return apiFetch("/training-requests/mine");
}

export function createPlannedTrainingRequest(idTraining) {
  return apiFetch("/training-requests/planned", {
    method: "POST",
    body: JSON.stringify({ id_training: idTraining }),
  });
}

export function createPersonalizedTrainingRequest(requestDesc) {
  return apiFetch("/training-requests/personalized", {
    method: "POST",
    body: JSON.stringify({ request_desc: requestDesc }),
  });
}
