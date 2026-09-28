import { apiFetch } from "./client";

export function searchEmployeesBySkills(requirements) {
  return apiFetch("/employees/search-by-skills", {
    method: "POST",
    body: JSON.stringify({ requirements }),
  });
}
