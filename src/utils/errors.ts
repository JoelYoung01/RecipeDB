import { ApiError } from "./api";
import { AuthApiError } from "./auth";

const FALLBACK = "Something went wrong. Please try again.";

function messageFromDetail(detail: unknown): string | null {
  if (typeof detail === "string" && detail.trim()) {
    return detail.trim();
  }
  if (detail && typeof detail === "object" && !Array.isArray(detail)) {
    const d = detail as Record<string, unknown>;
    for (const key of ["user_message", "message"] as const) {
      const value = d[key];
      if (typeof value === "string" && value.trim()) return value.trim();
    }
  }
  if (Array.isArray(detail) && detail.length) {
    const parts: string[] = [];
    for (const item of detail.slice(0, 3)) {
      if (item && typeof item === "object") {
        const msg =
          (item as { msg?: unknown; message?: unknown }).msg ??
          (item as { message?: unknown }).message;
        if (typeof msg === "string" && msg.trim()) parts.push(msg.trim());
      } else if (typeof item === "string" && item.trim()) {
        parts.push(item.trim());
      }
    }
    if (parts.length) return parts.join("; ");
  }
  return null;
}

/** Best-effort user-facing message from any thrown value. */
export function getErrorMessage(error: unknown, fallback = FALLBACK): string {
  if (error instanceof ApiError) {
    return error.userMessage || fallback;
  }
  if (error instanceof AuthApiError) {
    return error.message || fallback;
  }
  if (error instanceof Error && error.message.trim()) {
    // Strip leading "(401) " style prefixes from older formatting when present.
    const cleaned = error.message.replace(/^\(\d{3}\)\s*/, "").trim();
    return cleaned || fallback;
  }
  if (typeof error === "string" && error.trim()) {
    return error.trim();
  }
  return fallback;
}

export function parseApiErrorBody(body: unknown): {
  userMessage: string;
  detail: unknown;
  code?: string;
} {
  if (!body || typeof body !== "object") {
    return { userMessage: FALLBACK, detail: body };
  }

  const data = body as Record<string, unknown>;
  const detail = "detail" in data ? data.detail : body;

  const topLevel =
    typeof data.user_message === "string" && data.user_message.trim()
      ? data.user_message.trim()
      : null;

  const fromDetail = messageFromDetail(detail);
  const userMessage = topLevel || fromDetail || FALLBACK;
  const code = typeof data.code === "string" ? data.code : undefined;

  return { userMessage, detail, code };
}
