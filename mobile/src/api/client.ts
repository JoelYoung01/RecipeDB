import { API_URL } from "@/config";
import { queryClient } from "@/lib/query-client";
import { useSessionStore } from "@/stores/session";
import { parseApiErrorBody } from "./errors";

const NETWORK_MESSAGE = "Network error — check your connection and try again.";

export class ApiError extends Error {
  public status: number;
  public userMessage: string;
  public detail: unknown;
  public code?: string;

  constructor(
    message: string,
    status: number,
    options?: { userMessage?: string; detail?: unknown; code?: string }
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.userMessage = options?.userMessage || message;
    this.detail = options?.detail;
    this.code = options?.code;
  }
}

function resolveUrl(url: string): string {
  if (/^https?:\/\//i.test(url)) return url;
  return `${API_URL}${url.startsWith("/") ? "" : "/"}${url}`;
}

async function readErrorBody(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

/** Session expired / revoked — drop local session so the auth gate kicks in. */
function handleUnauthorized() {
  void useSessionStore.getState().clear();
  queryClient.clear();
}

export async function doFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const token = useSessionStore.getState().token;
  const headers: Record<string, string> = {
    ...((options?.headers as Record<string, string>) ?? {})
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(resolveUrl(url), { ...options, headers });
  } catch {
    throw new ApiError(NETWORK_MESSAGE, 503, { userMessage: NETWORK_MESSAGE });
  }

  if (!response.ok) {
    if (response.status === 401 && token) handleUnauthorized();
    const body = await readErrorBody(response);
    const parsed = parseApiErrorBody(body);
    throw new ApiError(parsed.userMessage, response.status, {
      userMessage: parsed.userMessage,
      detail: parsed.detail,
      code: parsed.code
    });
  }

  if (response.status === 204) return undefined as T;

  return (await response.json()) as T;
}

export async function get<T>(url: string): Promise<T> {
  return doFetch<T>(url);
}

export async function post<T>(url: string, body?: object): Promise<T> {
  return doFetch<T>(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {})
  });
}

export async function put<T>(url: string, body?: object): Promise<T> {
  return doFetch<T>(url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {})
  });
}

export async function patch<T>(url: string, body?: object): Promise<T> {
  return doFetch<T>(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {})
  });
}

export async function del(url: string): Promise<void> {
  await doFetch<void>(url, { method: "DELETE" });
}

export async function postFile<T>(url: string, file: FormData): Promise<T> {
  // Let fetch set the multipart boundary — do not set Content-Type manually.
  return doFetch<T>(url, { method: "POST", body: file });
}
