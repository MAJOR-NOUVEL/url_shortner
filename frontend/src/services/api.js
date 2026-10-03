const API_BASE = "";

export const getAuthToken = () => localStorage.getItem("bitroot_token") || localStorage.getItem("snipurl_token");
export const setAuthToken = (token) => {
  localStorage.setItem("bitroot_token", token);
  localStorage.setItem("snipurl_token", token);
};
export const removeAuthToken = () => {
  localStorage.removeItem("bitroot_token");
  localStorage.removeItem("snipurl_token");
};

const request = async (url, options = {}) => {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  const token = getAuthToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const errorMsg = data.message || data.error || (data.details ? data.details.map(d => d.message).join(", ") : "Request failed");
    throw new Error(errorMsg);
  }
  return data;
};

export const api = {
  // Auth
  register: (email, password) => request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password })
  }),
  login: (email, password) => request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  }),
  getCurrentUser: () => request("/api/auth/me"),

  // URLs
  createUrl: (url, custom_alias, expires_in_hours) => request("/api/urls", {
    method: "POST",
    body: JSON.stringify({
      url,
      custom_alias: custom_alias || null,
      expires_in_hours: expires_in_hours ? parseInt(expires_in_hours) : null
    })
  }),
  getMyUrls: () => request("/api/urls"),
  deleteUrl: (id) => request(`/api/urls/${id}`, { method: "DELETE" }),

  // Analytics & Health
  getUrlAnalytics: (id) => request(`/api/urls/${id}/analytics`),
  getHealth: () => request("/health")
};
