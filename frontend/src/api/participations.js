import { apiFetch } from "./client";

export function getParticipations() {
  return apiFetch("/participations");
}
