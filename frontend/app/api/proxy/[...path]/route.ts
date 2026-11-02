import { NextRequest, NextResponse } from "next/server";

const upstreamBase = process.env.API_INTERNAL_URL || "http://backend:8000";
const exact = new Set([
  "auth/csrf/", "auth/register/", "auth/login/", "auth/logout/", "auth/me/",
  "v2/cart/", "v2/checkout/", "v2/orders/", "v2/preorders/",
  "shipping/quote/", "commerce-control/shipping/lock/", "returns/",
]);
const dynamic = [
  /^v2\/products\/[0-9a-f-]{36}\/variants\/$/i,
  /^v2\/orders\/[0-9a-f-]{36}\/cancel\/$/i,
  /^v2\/preorders\/[0-9a-f-]{36}\/cancel\/$/i,
  /^orders\/[0-9a-f-]{36}\/(pay|tracking)\/$/i,
];

async function handler(req: NextRequest, context: {params: {path: string[]}}) {
  const {path} = context.params;
  const endpoint = path.join("/") + "/";
  if (!exact.has(endpoint) && !dynamic.some((pattern) => pattern.test(endpoint))) {
    return NextResponse.json({error: "Unknown API route"}, {status: 404});
  }
  const method = req.method;
  if (!["GET", "POST", "DELETE"].includes(method)) {
    return NextResponse.json({error: "Method not allowed"}, {status: 405});
  }
  const csrf = req.cookies.get("csrftoken")?.value;
  if (method !== "GET") {
    const origin = req.headers.get("origin");
    if (origin !== req.nextUrl.origin || !csrf || req.headers.get("x-csrftoken") !== csrf) {
      return NextResponse.json({error: "CSRF verification failed"}, {status: 403});
    }
  }
  const headers = new Headers({Accept: "application/json"});
  const cookie = req.headers.get("cookie");
  if (cookie) headers.set("Cookie", cookie);
  if (method !== "GET") {
    headers.set("Content-Type", "application/json");
    headers.set("X-CSRFToken", csrf || "");
    // Forward the browser's real origin. Django must explicitly trust it.
    headers.set("Origin", req.nextUrl.origin);
    headers.set("Referer", req.nextUrl.origin + "/");
  }
  try {
    const url = new URL(`/api/${endpoint}`, upstreamBase);
    url.search = req.nextUrl.search;
    const upstream = await fetch(url, {
      method, headers, body: method === "GET" ? undefined : await req.text(),
      cache: "no-store", redirect: "manual", signal: AbortSignal.timeout(20000),
    });
    const responseHeaders = new Headers({
      "Content-Type": upstream.headers.get("content-type") || "application/json",
      "Cache-Control": "no-store",
    });
    for (const cookieValue of upstream.headers.getSetCookie()) {
      responseHeaders.append("Set-Cookie", cookieValue);
    }
    return new NextResponse(await upstream.arrayBuffer(), {
      status: upstream.status, headers: responseHeaders,
    });
  } catch {
    return NextResponse.json({error: "Backend unavailable"}, {status: 502});
  }
}
export {handler as GET, handler as POST, handler as DELETE};