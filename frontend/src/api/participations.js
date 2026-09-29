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

export function getParticipationDocuments(idEmployee, idTraining) {
  return apiFetch(`/participations/${idEmployee}/${idTraining}/documents`);
}

export function uploadParticipationDocument(idEmployee, idTraining, documentType, file) {
  const body = new window.FormData();
  body.append("document_type", documentType);
  body.append("file", file);
  return apiFetch(`/participations/${idEmployee}/${idTraining}/documents`, {
    method: "POST",
    body,
  });
}

export function downloadParticipationDocument(idDocument) {
  return apiFetch(`/participations/document/${idDocument}/download`, { responseType: "blob" });
}

export function deleteParticipationDocument(idDocument) {
  return apiFetch(`/participations/document/${idDocument}`, { method: "DELETE" });
}
