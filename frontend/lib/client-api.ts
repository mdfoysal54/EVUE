export type CartItem = {variant_id: string; sku: string; product: string; quantity: number; price: string};
export type Order = {id: string; status: string; currency: string; total: string; expires_at: string};
function csrfToken(): string {
  const value = document.cookie.split("; ").find(x => x.startsWith("csrftoken="))?.split("=")[1] || "";
  return decodeURIComponent(value);
}
export async function api<T>(path: string, method: "GET" | "POST" | "DELETE" = "GET", body?: unknown): Promise<T> {
  if (method !== "GET" && !csrfToken()) {
    const csrfResponse = await fetch("/api/proxy/auth/csrf/", {credentials: "same-origin", cache: "no-store"});
    if (!csrfResponse.ok) throw new Error("Unable to initialize CSRF protection");
  }
  const response = await fetch(`/api/proxy/${path.replace(/^\/+/, "")}`, {
    method, credentials: "same-origin", cache: "no-store",
    headers: method === "GET" ? {} : {"Content-Type": "application/json", "X-CSRFToken": csrfToken()},
    body: method === "GET" ? undefined : JSON.stringify(body ?? {}),
  });
  const data = await response.json().catch(() => ({error: "Unexpected server response"}));
  if (!response.ok) throw new Error(typeof data.error === "string" ? data.error : data.detail || `HTTP ${response.status}`);
  return data as T;
}