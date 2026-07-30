import { API_URL } from "@/config";
import { useSessionStore } from "@/stores/session";
import { fetch as expoFetch } from "expo/fetch";
import { Platform } from "react-native";
import { ApiError } from "./client";
import { parseApiErrorBody } from "./errors";

export type SseHandler<T> = (event: T) => void;

type StreamingFetch = (
  url: string,
  init: {
    method: string;
    headers: Record<string, string>;
    body: string;
    signal?: AbortSignal;
  }
) => Promise<{
  ok: boolean;
  status: number;
  json(): Promise<unknown>;
  body: { getReader(): { read(): Promise<{ done: boolean; value?: Uint8Array }> } } | null;
}>;

/**
 * Native fetch (RN) does not expose streaming bodies; `expo/fetch` does.
 * On web the standard fetch already streams.
 */
const streamingFetch: StreamingFetch =
  Platform.OS === "web"
    ? (globalThis.fetch.bind(globalThis) as unknown as StreamingFetch)
    : (expoFetch as unknown as StreamingFetch);

/** POST and consume a text/event-stream body as JSON `data:` frames. */
export async function postSse<T extends { status?: string }>(
  url: string,
  body: object | undefined,
  onEvent: SseHandler<T>,
  signal?: AbortSignal
): Promise<void> {
  const token = useSessionStore.getState().token;
  const fullUrl = /^https?:\/\//i.test(url)
    ? url
    : `${API_URL}${url.startsWith("/") ? "" : "/"}${url}`;

  const response = await streamingFetch(fullUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify(body ?? {}),
    signal
  });

  if (!response.ok) {
    let errorBody: unknown = null;
    try {
      errorBody = await response.json();
    } catch {
      errorBody = null;
    }
    const parsed = parseApiErrorBody(errorBody);
    throw new ApiError(parsed.userMessage, response.status, {
      userMessage: parsed.userMessage,
      detail: parsed.detail,
      code: parsed.code
    });
  }

  if (!response.body) {
    throw new Error("No response body for SSE stream");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let done = false;

  while (!done) {
    const result = await reader.read();
    done = result.done;
    if (done) break;
    buffer += decoder.decode(result.value, { stream: true } as TextDecodeOptions);
    buffer = consumeSseBuffer(buffer, onEvent);
  }
}

/**
 * Split completed `\n\n`-terminated frames out of the buffer, dispatch their
 * JSON `data:` payloads, and return the unconsumed remainder.
 */
export function consumeSseBuffer<T>(buffer: string, onEvent: SseHandler<T>): string {
  const chunks = buffer.split("\n\n");
  const rest = chunks.pop() ?? "";
  for (const chunk of chunks) {
    for (const line of chunk.split("\n")) {
      if (!line.startsWith("data:")) continue;
      const raw = line.slice(5).trim();
      if (!raw) continue;
      try {
        onEvent(JSON.parse(raw) as T);
      } catch {
        // ignore malformed frames
      }
    }
  }
  return rest;
}
