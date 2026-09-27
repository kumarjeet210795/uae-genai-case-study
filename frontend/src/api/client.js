const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(url, options = {}) {
  const r = await fetch(`${API}${url}`, options);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function login(username) {
  return request("/auth/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username})
  });
}

export async function chat(token, message, conversationId) {
  return request("/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json", "Authorization": `Bearer ${token}`},
    body: JSON.stringify({message, conversation_id: conversationId})
  });
}

export async function decideApproval(token, approvalId, decision) {
  return request(`/approvals/${approvalId}/decision`, {
    method: "POST",
    headers: {"Content-Type": "application/json", "Authorization": `Bearer ${token}`},
    body: JSON.stringify({decision})
  });
}
