import { NextRequest, NextResponse } from "next/server";

interface NewsletterRequestBody {
  consent?: boolean;
  email?: string;
}

const API_BASE_URL =
  process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";

const MAX_EMAIL_LENGTH = 254;
const REQUEST_TIMEOUT_MS = 8000;

export async function POST(req: NextRequest) {
  // Origin verification (CSRF protection)
  const origin = req.headers.get("origin");
  if (origin !== req.nextUrl.origin) {
    return NextResponse.json(
      { error: "Invalid origin" },
      { status: 403 }
    );
  }

  // Parse request body
  let data: NewsletterRequestBody;
  try {
    data = await req.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON" },
      { status: 400 }
    );
  }

  // Input validation
  const isValidEmail =
    typeof data.email === "string" &&
    data.email.trim().length > 0 &&
    data.email.length <= MAX_EMAIL_LENGTH;

  if (!isValidEmail || data.consent !== true) {
    return NextResponse.json(
      { error: "Email and consent required" },
      { status: 400 }
    );
  }

  // Forward to upstream backend service
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/operations/newsletter/subscribe/`,
      {
        body: JSON.stringify({
          consent: data.consent,
          email: data.email.trim(),
        }),
        cache: "no-store",
        headers: {
          "Content-Type": "application/json",
        },
        method: "POST",
        signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
      }
    );

    const payload = await response.json();
    return NextResponse.json(payload, { status: response.status });
  } catch {
    return NextResponse.json(
      { error: "Service unavailable" },
      { status: 503 }
    );
  }
}