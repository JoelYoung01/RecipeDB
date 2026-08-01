import { API_URL } from "@/config";
import type { UserResponse } from "@/types";

/** Auth endpoints — ported from the web app's src/utils/auth.ts. */

export type AuthRedirectPayload = {
  code: string;
  message: string;
  redirect_to: string;
  email?: string | null;
  dev_otp?: string | null;
};

export type TokenPayload = {
  access_token: string;
  user: UserResponse;
};

export class AuthApiError extends Error {
  status: number;
  detail: unknown;
  redirectTo?: string;
  email?: string;
  devOtp?: string | null;

  constructor(
    message: string,
    options: {
      status: number;
      detail?: unknown;
      redirectTo?: string;
      email?: string;
      devOtp?: string | null;
    }
  ) {
    super(message);
    this.name = "AuthApiError";
    this.status = options.status;
    this.detail = options.detail;
    this.redirectTo = options.redirectTo;
    this.email = options.email;
    this.devOtp = options.devOtp;
  }
}

function parseDetail(
  detail: unknown,
  body?: Record<string, unknown> | null
): {
  message: string;
  redirectTo?: string;
  email?: string;
  code?: string;
  devOtp?: string | null;
} {
  const topMessage =
    typeof body?.user_message === "string" && body.user_message.trim()
      ? body.user_message.trim()
      : null;

  if (typeof detail === "string") {
    return { message: topMessage || detail };
  }
  if (detail && typeof detail === "object") {
    const d = detail as Record<string, unknown>;
    const nestedMessage =
      (typeof d.user_message === "string" && d.user_message) ||
      (typeof d.message === "string" && d.message) ||
      null;
    return {
      message: topMessage || nestedMessage || "Request failed",
      redirectTo: typeof d.redirect_to === "string" ? d.redirect_to : undefined,
      email: typeof d.email === "string" ? d.email : undefined,
      code:
        (typeof body?.code === "string" && body.code) ||
        (typeof d.code === "string" ? d.code : undefined),
      devOtp: typeof d.dev_otp === "string" ? d.dev_otp : null
    };
  }
  return { message: topMessage || "Request failed" };
}

async function readAuthResponse(response: Response) {
  const text = await response.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }
  return data as Record<string, unknown> | null;
}

/**
 * Verify a stored session token.
 * Returns a refreshed payload, `null` when the session is rejected, and
 * throws on transient failures (offline, 5xx) so callers can keep the session.
 */
export async function checkSessionToken(accessToken: string): Promise<TokenPayload | null> {
  const response = await fetch(`${API_URL}/auth/verify-session/`, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  if (response.ok) return (await response.json()) as TokenPayload;
  if (response.status === 401 || response.status === 403) return null;
  throw new Error(`verify-session failed with status ${response.status}`);
}

export async function loginWithPassword(payload: {
  email: string;
  password: string;
}): Promise<TokenPayload> {
  const response = await fetch(`${API_URL}/auth/login/`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await readAuthResponse(response);

  if (response.status === 403) {
    // Unverified account — server directs the client to the verify page.
    const parsed = parseDetail(data?.detail, data);
    throw new AuthApiError(parsed.message || "Email not verified", {
      status: 403,
      detail: data?.detail,
      redirectTo: parsed.redirectTo || response.headers.get("Location") || undefined,
      email: parsed.email,
      devOtp: parsed.devOtp
    });
  }

  if (!response.ok) {
    const parsed = parseDetail(data?.detail ?? data, data);
    throw new AuthApiError(parsed.message || "Login failed", {
      status: response.status,
      detail: data?.detail
    });
  }

  return data as unknown as TokenPayload;
}

export async function registerWithPassword(payload: {
  email: string;
  password: string;
  display_name: string;
}): Promise<AuthRedirectPayload> {
  const response = await fetch(`${API_URL}/auth/register/`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await readAuthResponse(response);
  if (!response.ok) {
    const parsed = parseDetail(data?.detail ?? data, data);
    throw new AuthApiError(parsed.message, { status: response.status, detail: data?.detail });
  }
  return data as unknown as AuthRedirectPayload;
}

export async function verifyEmailOtp(payload: {
  email: string;
  otp: string;
}): Promise<TokenPayload> {
  const response = await fetch(`${API_URL}/auth/verify-email/`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await readAuthResponse(response);
  if (!response.ok) {
    const parsed = parseDetail(data?.detail ?? data, data);
    throw new AuthApiError(parsed.message || "Verification failed", {
      status: response.status,
      detail: data?.detail
    });
  }
  return data as unknown as TokenPayload;
}

export async function resendVerificationEmail(email: string): Promise<AuthRedirectPayload> {
  const response = await fetch(`${API_URL}/auth/resend-verification/`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ email })
  });
  const data = await readAuthResponse(response);
  if (!response.ok) {
    const parsed = parseDetail(data?.detail ?? data, data);
    throw new AuthApiError(parsed.message || "Could not resend code", {
      status: response.status,
      detail: data?.detail
    });
  }
  return data as unknown as AuthRedirectPayload;
}

/** Exchange a Google ID token for a Sous Kit session. */
export async function loginWithGoogle(payload: { credential: string }): Promise<TokenPayload> {
  const response = await fetch(`${API_URL}/auth/login-google/`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await readAuthResponse(response);
  if (!response.ok) {
    const parsed = parseDetail(data?.detail ?? data, data);
    throw new AuthApiError(parsed.message || "Google sign-in failed", {
      status: response.status,
      detail: data?.detail
    });
  }
  return data as unknown as TokenPayload;
}

/**
 * Exchange a Sign in with Apple identity token for a Sous Kit session.
 * `full_name` is only available on the FIRST authorization — Apple never
 * repeats it — so pass it along whenever present.
 */
export async function loginWithApple(payload: {
  identity_token: string;
  full_name?: string | null;
}): Promise<TokenPayload> {
  const response = await fetch(`${API_URL}/auth/login-apple/`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await readAuthResponse(response);
  if (!response.ok) {
    const parsed = parseDetail(data?.detail ?? data, data);
    throw new AuthApiError(parsed.message || "Apple sign-in failed", {
      status: response.status,
      detail: data?.detail
    });
  }
  return data as unknown as TokenPayload;
}
