const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:18000";


async function parseError(response) {
  let message = `Request failed with status ${response.status}`;

  try {
    const body = await response.json();

    if (typeof body.detail === "string") {
      message = body.detail;
    } else if (Array.isArray(body.detail)) {
      message = body.detail
        .map((item) => item.msg)
        .join(", ");
    } else if (body.message) {
      message = body.message;
    }
  } catch {
    // Keep the default error message.
  }

  return message;
}


async function request(
  path,
  options = {},
) {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    options,
  );

  if (!response.ok) {
    const message = await parseError(
      response,
    );

    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}


export async function getHealth() {
  return request("/health");
}


export async function listIncidents(
  filters = {},
) {
  const params = new URLSearchParams();

  if (filters.service) {
    params.set(
      "service",
      filters.service,
    );
  }

  if (filters.severity) {
    params.set(
      "severity",
      filters.severity,
    );
  }

  params.set("limit", "200");

  const query = params.toString();

  return request(
    `/api/incidents${query ? `?${query}` : ""}`,
  );
}


export async function createIncident(
  payload,
) {
  return request(
    "/api/incidents",
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(payload),
    },
  );
}


export async function deleteIncident(
  incidentId,
) {
  return request(
    `/api/incidents/${incidentId}`,
    {
      method: "DELETE",
    },
  );
}


export async function uploadDocument({
  file,
  title,
  documentType,
  incidentId,
  service,
}) {
  const formData = new FormData();

  formData.append(
    "file",
    file,
  );

  if (title.trim()) {
    formData.append(
      "title",
      title.trim(),
    );
  }

  formData.append(
    "document_type",
    documentType.trim() || "runbook",
  );

  if (incidentId) {
    formData.append(
      "incident_id",
      incidentId,
    );
  }

  if (service.trim()) {
    formData.append(
      "service",
      service.trim(),
    );
  }

  return request(
    "/api/documents/upload",
    {
      method: "POST",
      body: formData,
    },
  );
}


export async function searchSimilarIncidents(
  payload,
) {
  return request(
    "/api/search/similar",
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(payload),
    },
  );
}


export async function askRag(
  payload,
) {
  return request(
    "/api/rag/ask",
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(payload),
    },
  );
}


export {
  API_BASE_URL,
};