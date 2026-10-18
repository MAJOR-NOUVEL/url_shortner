const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

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

  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("text/html")) {
    throw new Error(
      API_BASE
        ? "Received HTML response instead of JSON. The backend server might be starting up or encountered an error."
        : "Backend API not reachable. Please ensure VITE_API_BASE_URL is set in Vercel project environment variables."
    );
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const errorMsg = data.message || data.error || (data.details ? data.details.map(d => d.message).join(", ") : "Request failed");
    const err = new Error(errorMsg);
    err.status = res.status;
    throw err;
  }
  return data;
};

export const getFullShortUrl = (shortUrl, shortCode) => {
  if (!shortUrl || shortUrl.includes("localhost") || shortUrl.includes("127.0.0.1") || shortUrl.startsWith("/")) {
    if (typeof window !== "undefined" && window.location?.origin) {
      return `${window.location.origin}/${shortCode}`;
    }
  }
  return shortUrl;
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
  resolveUrl: (code) => request(`/api/urls/resolve/${code}`),
  deleteUrl: (id) => request(`/api/urls/${id}`, { method: "DELETE" }),

  // Analytics & Health
  getUrlAnalytics: (id) => request(`/api/urls/${id}/analytics`),
  getHealth: () => request("/health")
};
