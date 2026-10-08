// Dynamically resolve API base: relative for same-origin production, localhost:8000 for Vite dev server
const API_BASE = (typeof window !== "undefined" && window.location.port === "3000") ? "http://127.0.0.1:8000" : "";

export function getAuthHeaders() {
  const token = localStorage.getItem("connectme_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    ...getAuthHeaders(),
    ...(options.headers || {}),
  };

  const config = {
    ...options,
    headers,
  };

  const response = await fetch(url, config);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data.detail || (Array.isArray(data.detail) ? data.detail[0]?.msg : null) || "An error occurred";
    const error = new Error(errorMsg);
    error.status = response.status;
    error.detail = data.detail;
    throw error;
  }

  return data;
}

// Authentication APIs
export async function loginUser(username, password) {
  return apiRequest("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
}

export async function registerUser(payload) {
  return apiRequest("/api/v1/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function getMe() {
  return apiRequest("/api/v1/auth/me");
}

// Profile APIs
export async function getMyProfile() {
  return apiRequest("/api/v1/users/me");
}

export async function updateMyProfile(payload) {
  return apiRequest("/api/v1/users/me", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function getUserProfile(userId) {
  return apiRequest(`/api/v1/users/${userId}`);
}

// Social Graph APIs
export async function followUser(userId) {
  return apiRequest(`/api/v1/users/${userId}/follow`, {
    method: "POST",
  });
}

export async function unfollowUser(userId) {
  return apiRequest(`/api/v1/users/${userId}/unfollow`, {
    method: "POST",
  });
}

// Posts and Feed APIs
export async function getFeed() {
  return apiRequest("/api/v1/posts/feed");
}

export async function createPost(formData) {
  const url = `${API_BASE}/api/v1/posts`;
  const headers = {
    ...getAuthHeaders(),
  };

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: formData,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const errorMsg = data.detail || "Upload failed";
    const error = new Error(errorMsg);
    error.status = response.status;
    throw error;
  }

  return data;
}

export async function deletePost(postId) {
  return apiRequest(`/api/v1/posts/${postId}`, {
    method: "DELETE",
  });
}

// Interactions APIs
export async function toggleLike(postId) {
  return apiRequest(`/api/v1/posts/${postId}/like`, {
    method: "POST",
  });
}

export async function getComments(postId) {
  return apiRequest(`/api/v1/posts/${postId}/comments`);
}

export async function addComment(postId, commentText) {
  return apiRequest(`/api/v1/posts/${postId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment_text: commentText }),
  });
}
