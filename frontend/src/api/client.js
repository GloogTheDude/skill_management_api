const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8001").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `Request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      ...(options.body && !(options.body instanceof window.FormData) ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    let detail;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : undefined;
    } catch {
      // Keep the HTTP status when the server has no JSON error body.
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return null;
  if (options.responseType === "blob") return response.blob();
  return response.json();
}
