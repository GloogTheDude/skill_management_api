import { apiFetch } from "./client";

export function getDomaines() { return apiFetch("/domaine"); }
export function getTrainingSources() { return apiFetch("/training_source"); }
export function getSkills() { return apiFetch("/skill"); }
export function getDiplomas() { return apiFetch("/diploma"); }
export function getCertifications() { return apiFetch("/certification"); }
