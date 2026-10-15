import { NextRequest, NextResponse } from "next/server";
const API = process.env.API_INTERNAL_URL || "http://backend:8000";
const allowed = new Set(["auth/csrf/", "auth/register/", "auth/login/", "auth/logout/", "auth/me/", "commerce/cart/", "commerce/orders/"]);
const uuidDetail = /^commerce\/orders\/[0-9a-fA-F-]{36}\/$/;
async function handler(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const endpoint = path.join("/") + "/";
  if (!allowed.has(endpoint) && !uuidDetail.test(endpoint)) return NextResponse.json({ error: "Not found" }, { status: 404 });
  const method = request.method;
  if (method !== "GET" && method !== "POST" && method !== "DELETE") return NextResponse.json({error:"Method not allowed"},{status:405});
  // Restrict same-origin state-changing calls, and forward the Django CSRF token.
  if (method !== "GET") {
    const origin = request.headers.get("origin");
    if (!origin || origin !== request.nextUrl.origin) return NextResponse.json({error:"Invalid origin"},{status:403});
    const csrfCookie = request.cookies.get("csrftoken")?.value;
    const csrfHeader = request.headers.get("x-csrftoken");
    if (!csrfCookie || csrfHeader !== csrfCookie) return NextResponse.json({error:"CSRF verification failed"},{status:403});
  }
  const headers = new Headers({ Accept: "application/json" });
  const cookie = request.headers.get("cookie");
  if (cookie) headers.set("cookie",cookie);
  if (method !== "GET") {
    headers.set("Content-Type","application/json");
    headers.set("X-CSRFToken",request.headers.get("x-csrftoken") || "");
    headers.set("Origin",API);
  }
  try {
    const upstream = await fetch(`${API}/api/${endpoint}`, { method, headers, body: method === "GET" ? undefined : await request.text(), cache: "no-store", redirect: "manual" });
    const responseHeaders = new Headers({"content-type": upstream.headers.get("content-type") || "application/json", "cache-control":"no-store"});
    // Forward Django's session and CSRF cookies, retaining HttpOnly on sessions.
    for (const value of upstream.headers.getSetCookie()) responseHeaders.append("set-cookie", value);
    return new NextResponse(await upstream.arrayBuffer(), {status: upstream.status, headers: responseHeaders});
  } catch {
    return NextResponse.json({error:"Backend unavailable"},{status:502});
  }
}
export { handler as GET, handler as POST, handler as DELETE };
