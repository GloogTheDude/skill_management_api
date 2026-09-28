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

export function getManagerPendingTrainingRequests() {
  return apiFetch("/training-requests/pending/manager");
}

export function getHrPendingTrainingRequests() {
  return apiFetch("/training-requests/pending/hr");
}

export function approveTrainingRequest(idTrainingRequest, idTraining = null) {
  return apiFetch(`/training-requests/${idTrainingRequest}/approve`, {
    method: "POST",
    body: JSON.stringify(idTraining === null ? {} : { id_training: idTraining }),
  });
}

export function rejectTrainingRequest(idTrainingRequest, reason) {
  return apiFetch(`/training-requests/${idTrainingRequest}/reject`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}
